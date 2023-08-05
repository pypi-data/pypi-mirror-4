# -*- coding: utf-8 -*-
import logging


logger = logging.getLogger(__name__)


class OleStorageTestMixin(object):

    hwp5file_name = 'sample-5017.hwp'
    OleStorage = None

    def get_fixture_file(self, filename):
        from hwp5.tests import get_fixture_path
        return get_fixture_path(filename)

    @property
    def hwp5file_path(self):
        return self.get_fixture_file(self.hwp5file_name)

    @property
    def olestg(self):
        return self.OleStorage(self.hwp5file_path)

    def test_OleStorage(self):
        if self.OleStorage is None:
            logger.warning('%s: skipped', self.id())
            return
        OleStorage = self.OleStorage
        from hwp5.errors import InvalidOleStorageError
        from hwp5.storage import is_storage

        olestg = OleStorage(self.hwp5file_path)
        self.assertTrue(is_storage(olestg))
        self.assertTrue(isinstance(olestg, OleStorage))

        nonolefile = self.get_fixture_file('nonole.txt')
        self.assertRaises(InvalidOleStorageError, OleStorage, nonolefile)

    def test_getitem0(self):
        if self.OleStorage is None:
            logger.warning('%s: skipped', self.id())
            return
        from hwp5.storage import is_storage, is_stream
        olestg = self.olestg
        self.assertTrue(is_storage(olestg))
        #self.assertEquals('', olestg.path)

        docinfo = olestg['DocInfo']
        self.assertTrue(is_stream(docinfo))
        #self.assertEquals('DocInfo', docinfo.path)

        bodytext = olestg['BodyText']
        self.assertTrue(is_storage(bodytext))
        #self.assertEquals('BodyText', bodytext.path)

        section = bodytext['Section0']
        self.assertTrue(is_stream(section))
        #self.assertEquals('BodyText/Section0', section.path)

        f = section.open()
        try:
            data = f.read()
            self.assertEquals(1529, len(data))
        finally:
            f.close()

        try:
            bodytext['nonexists']
            self.fail('KeyError expected')
        except KeyError:
            pass

    def test_init_should_receive_string_olefile(self):
        if self.OleStorage is None:
            logger.warning('%s: skipped', self.id())
            return
        OleStorage = self.OleStorage
        path = self.get_fixture_file(self.hwp5file_name)
        olestg = OleStorage(path)
        self.assertTrue(olestg['FileHeader'] is not None)

    def test_iter(self):
        if self.OleStorage is None:
            logger.warning('%s: skipped', self.id())
            return
        olestg = self.olestg
        gen = iter(olestg)
        #import types
        #self.assertTrue(isinstance(gen, types.GeneratorType))
        expected = ['FileHeader', 'BodyText', 'BinData', 'Scripts',
                    'DocOptions', 'DocInfo', 'PrvText', 'PrvImage',
                    '\x05HwpSummaryInformation']
        self.assertEquals(sorted(expected), sorted(gen))

    def test_getitem(self):
        if self.OleStorage is None:
            logger.warning('%s: skipped', self.id())
            return
        from hwp5.storage import is_storage
        #from hwp5.storage.ole import OleStorage
        olestg = self.olestg

        try:
            olestg['non-exists']
            self.fail('KeyError expected')
        except KeyError:
            pass

        fileheader = olestg['FileHeader']
        self.assertTrue(hasattr(fileheader, 'open'))

        bindata = olestg['BinData']
        self.assertTrue(is_storage(bindata))
        #self.assertEquals('BinData', bindata.path)

        self.assertEquals(sorted(['BIN0002.jpg', 'BIN0002.png',
                                  'BIN0003.png']),
                          sorted(iter(bindata)))

        bin0002 = bindata['BIN0002.jpg']
        self.assertTrue(hasattr(bin0002, 'open'))

    def test_iter_storage_leafs(self):
        if self.OleStorage is None:
            logger.warning('%s: skipped', self.id())
            return
        from hwp5.storage import iter_storage_leafs
        result = iter_storage_leafs(self.olestg)
        expected = ['\x05HwpSummaryInformation', 'BinData/BIN0002.jpg',
                    'BinData/BIN0002.png', 'BinData/BIN0003.png',
                    'BodyText/Section0', 'DocInfo', 'DocOptions/_LinkDoc',
                    'FileHeader', 'PrvImage', 'PrvText',
                    'Scripts/DefaultJScript', 'Scripts/JScriptVersion']
        self.assertEquals(sorted(expected), sorted(result))

    def test_unpack(self):
        if self.OleStorage is None:
            logger.warning('%s: skipped', self.id())
            return
        from hwp5.storage import unpack
        import shutil
        import os
        import os.path

        if os.path.exists('5017'):
            shutil.rmtree('5017')
        os.mkdir('5017')
        unpack(self.olestg, '5017')

        self.assertTrue(os.path.exists('5017/_05HwpSummaryInformation'))
        self.assertTrue(os.path.exists('5017/BinData/BIN0002.jpg'))
        self.assertTrue(os.path.exists('5017/BinData/BIN0002.png'))
        self.assertTrue(os.path.exists('5017/BinData/BIN0003.png'))
        self.assertTrue(os.path.exists('5017/BodyText/Section0'))
        self.assertTrue(os.path.exists('5017/DocInfo'))
        self.assertTrue(os.path.exists('5017/DocOptions/_LinkDoc'))
        self.assertTrue(os.path.exists('5017/FileHeader'))
        self.assertTrue(os.path.exists('5017/PrvImage'))
        self.assertTrue(os.path.exists('5017/PrvText'))
        self.assertTrue(os.path.exists('5017/Scripts/DefaultJScript'))
        self.assertTrue(os.path.exists('5017/Scripts/JScriptVersion'))
