"""Private covers: actual JPEG generation and cached path-signing contract."""
import asyncio
import importlib.util
import sys
import tempfile
import time
import types
import unittest
from pathlib import Path
from unittest.mock import Mock, patch
from PIL import Image


def load_catalog():
    names = ['homeassistant', 'homeassistant.core', 'homeassistant.helpers',
             'homeassistant.helpers.aiohttp_client', 'homeassistant.components',
             'homeassistant.components.http', 'homeassistant.components.http.auth']
    modules = {name: types.ModuleType(name) for name in names}
    modules['homeassistant.core'].HomeAssistant = object
    modules['homeassistant.helpers.aiohttp_client'].async_get_clientsession = Mock()
    modules['homeassistant.components.http.auth'].async_sign_path = Mock()
    path = Path(__file__).parents[1] / 'custom_components/nature_frame/catalog.py'
    spec = importlib.util.spec_from_file_location('test_nature_catalog', path)
    module = importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules, {**modules, spec.name: module}):
        spec.loader.exec_module(module)
    return module


catalog = load_catalog()


class PrivateCoverTest(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        self.roots = patch.multiple(catalog, LOCAL_MEDIA_ROOT=root,
            PRIVATE_MEDIA_ROOT=root/'nature-frame/private',
            PRIVATE_PREVIEW_ROOT=root/'nature-frame/previews/private')
        self.roots.start()
        folder = catalog.PRIVATE_MEDIA_ROOT/'Zoo Private'
        folder.mkdir(parents=True)
        self.image = folder/'Flodhest med æøå og mellemrum.png'
        Image.new('RGBA', (120, 240), (90, 30, 120, 180)).save(self.image)
        async def executor(func, *args):
            return func(*args)
        self.hass = types.SimpleNamespace(async_add_executor_job=executor)
        self.library = catalog.NatureFrameCatalog(self.hass)
        remote = catalog.NatureGallery('birds','Birds','test',(),())
        self.library._remote_galleries = {'birds':remote}
        self.library._last_refresh = time.monotonic()
        self.signer = Mock(side_effect=lambda hass,path,expiration,**kw: path+'?authSig=test-'+str(self.signer.call_count))
        self.sign_patch = patch.object(catalog,'async_sign_path',self.signer)
        self.sign_patch.start()

    async def asyncTearDown(self):
        self.sign_patch.stop(); self.roots.stop(); self.temp.cleanup()

    async def test_private_preview_is_a_signed_browser_safe_jpeg(self):
        await self.library.async_refresh()
        thumb = self.library.gallery('private-zoo').thumbnail
        self.assertTrue(thumb.startswith('/media/local/nature-frame/previews/private/private-zoo-'))
        self.assertIn('?authSig=',thumb)
        args,kwargs = self.signer.call_args
        self.assertEqual(kwargs, {'use_content_user':True})
        self.assertEqual(args[2].total_seconds(),2*86400)
        with Image.open(next(catalog.PRIVATE_PREVIEW_ROOT.glob('*.jpg'))) as image:
            self.assertEqual(image.format,'JPEG'); self.assertEqual(image.mode,'RGB')

    async def test_entity_refresh_keeps_the_same_signed_cover(self):
        await self.library.async_refresh(); first = self.library.gallery('private-zoo').thumbnail
        self.library._last_private_refresh = 0
        await self.library.async_refresh()
        self.assertEqual(self.library.gallery('private-zoo').thumbnail,first)
        self.assertEqual(self.signer.call_count,1)

    async def test_signature_is_renewed_before_it_expires(self):
        await self.library.async_refresh(); first = self.library.gallery('private-zoo').thumbnail
        self.library._signed_covers = {p:(0,url) for p,(_,url) in self.library._signed_covers.items()}
        await self.library.async_refresh()
        self.assertNotEqual(self.library.gallery('private-zoo').thumbnail,first)
        self.assertEqual(self.signer.call_count,2)

    async def test_replaced_image_updates_cover_and_discards_old_signature(self):
        await self.library.async_refresh(); first = self.library.gallery('private-zoo').thumbnail
        Image.new('RGB',(160,80),'green').save(self.image)
        self.library._last_private_refresh = 0
        await self.library.async_refresh()
        self.assertNotEqual(self.library.gallery('private-zoo').thumbnail,first)
        self.assertEqual(len(self.library._signed_covers),1)
        self.assertEqual(len(list(catalog.PRIVATE_PREVIEW_ROOT.glob('*.jpg'))),1)

    async def test_empty_private_collection_has_no_broken_thumbnail(self):
        self.image.unlink()
        await self.library.async_refresh()
        self.assertIsNone(self.library.gallery('private-zoo').thumbnail)
        self.signer.assert_not_called()
