#
# Unit Tests for ModelData objects
#

import os
import sys
from os.path import abspath, dirname
coopr_dir=dirname(dirname(abspath(__file__)))+os.sep+".."+os.sep+".."
sys.path.insert(0, coopr_dir)
from coopr.pyomo import *
import coopr
import pyutilib.common
import pyutilib.th as unittest
from coopr.pyomo.base.plugin import DataManagerFactory

currdir=dirname(abspath(__file__))+os.sep
example_dir=coopr_dir+os.sep+".."+os.sep+"examples"+os.sep+"pyomo"+os.sep+"tutorials"+os.sep+"tab"+os.sep
csv_dir=coopr_dir+os.sep+".."+os.sep+"examples"+os.sep+"pyomo"+os.sep+"tutorials"+os.sep+"csv"+os.sep
tutorial_dir=coopr_dir+os.sep+".."+os.sep+"examples"+os.sep+"pyomo"+os.sep+"tutorials"+os.sep

xls_interface = not DataManagerFactory('xls') is None
xlsx_interface = not DataManagerFactory('xlsx') is None
xlsb_interface = not DataManagerFactory('xlsb') is None
xlsm_interface = not DataManagerFactory('xlsm') is None


class PyomoTableData(unittest.TestCase):

    def setUp(self):
        pass

    def construct(self,filename):
        pass

    def test_read_set(self):
        td = DataManagerFactory('xls')
        td.initialize(currdir+"Book1.xls", range="TheRange", format='set', set="X")
        try:
            td.open()
            td.read()
            td.close()
            self.assertEqual( td._info, ['set', 'X', ':=', 'A1', 2.0, 3.0, 4.0, 'A5', 6.0, 7.0, 8.0, 'A9', 10.0, 11.0, 12.0, 'A13', 14.0, 15.0, 16.0])
        except pyutilib.common.ApplicationError:
            pass

    def test_read_param1(self):
        td = DataManagerFactory('xls')
        td.initialize(currdir+"Book1.xls", range="TheRange", index=['aa'], param=['bb','cc','dd'])
        try:
            td.open()
            td.read()
            td.close()
            self.assertEqual( td._info, ['param', ':', 'bb', 'cc', 'dd', ':=', 'A1', 2.0, 3.0, 4.0, 'A5', 6.0, 7.0, 8.0, 'A9', 10.0, 11.0, 12.0, 'A13', 14.0, 15.0, 16.0])
        except pyutilib.common.ApplicationError:
            pass

    def test_read_param2(self):
        td = DataManagerFactory('xls')
        td.initialize(currdir+"Book1.xls",range="TheRange", index_name="X", index=['aa'], param=['bb','cc','dd'])
        try:
            td.open()
            td.read()
            td.close()
            self.assertEqual( td._info, ['param', ':', 'X', ':', 'bb', 'cc', 'dd', ':=', 'A1', 2.0, 3.0, 4.0, 'A5', 6.0, 7.0, 8.0, 'A9', 10.0, 11.0, 12.0, 'A13', 14.0, 15.0, 16.0])
        except pyutilib.common.ApplicationError:
            pass

    def test_read_param3(self):
        td = DataManagerFactory('xls')
        td.initialize(currdir+"Book1.xls",range="TheRange", index_name="X", index=['aa','bb','cc'], param=["dd"], param_name={'dd':'a'})
        try:
            td.open()
            td.read()
            td.close()
            self.assertEqual( td._info, ['param', ':', 'X', ':', 'a', ':=', 'A1', 2.0, 3.0, 4.0, 'A5', 6.0, 7.0, 8.0, 'A9', 10.0, 11.0, 12.0, 'A13', 14.0, 15.0, 16.0])
        except pyutilib.common.ApplicationError:
            pass

    def test_read_param4(self):
        td = DataManagerFactory('xls')
        td.initialize(currdir+"Book1.xls",range="TheRange", index_name="X", index=['aa','bb'], param=['cc','dd'], param_name={'cc':'a', 'dd':'b'})
        try:
            td.open()
            td.read()
            td.close()
            self.assertEqual( td._info, ['param', ':', 'X', ':', 'a', 'b', ':=', 'A1', 2.0, 3.0, 4.0, 'A5', 6.0, 7.0, 8.0, 'A9', 10.0, 11.0, 12.0, 'A13', 14.0, 15.0, 16.0])
        except pyutilib.common.ApplicationError:
            pass

    def test_read_array1(self):
        td = DataManagerFactory('xls')
        td.initialize(currdir+"Book1.xls",range="TheRange", param="X", format="array")
        try:
            td.open()
            td.read()
            td.close()
            self.assertEqual( td._info, ['param', 'X', ':', 'bb', 'cc', 'dd', ':=', 'A1', 2.0, 3.0, 4.0, 'A5', 6.0, 7.0, 8.0, 'A9', 10.0, 11.0, 12.0, 'A13', 14.0, 15.0, 16.0])
        except pyutilib.common.ApplicationError:
            pass

    def test_read_array2(self):
        td = DataManagerFactory('xls')
        td.initialize(currdir+"Book1.xls",range="TheRange",param="X",format="transposed_array")
        try:
            td.open()
            td.read()
            td.close()
            self.assertEqual( td._info, ['param', 'X', '(tr)',':', 'bb', 'cc', 'dd', ':=', 'A1', 2.0, 3.0, 4.0, 'A5', 6.0, 7.0, 8.0, 'A9', 10.0, 11.0, 12.0, 'A13', 14.0, 15.0, 16.0])
        except pyutilib.common.ApplicationError:
            pass

    def test_error1(self):
        td = DataManagerFactory('xls')
        td.initialize("bad")
        try:
            td.open()
            self.fail("Expected IOError because of bad file")
        except IOError:
            pass

    def test_error2(self):
        td = DataManagerFactory('xls')
        try:
            td.open()
            self.fail("Expected IOError because no file specified")
        except (IOError,AttributeError):
            pass

    def test_error3(self):
        td = DataManagerFactory('txt')
        try:
            td.initialize(currdir+"display.txt")
            td.open()
            self.fail("Expected IOError because of bad file type")
        except (IOError, AttributeError):
            pass

    def test_error4(self):
        td = DataManagerFactory('txt')
        try:
            td.initialize(filename=currdir+"dummy")
            td.open()
            self.fail("Expected IOError because of bad file type")
        except (IOError, AttributeError):
            pass

    def test_error5(self):
        td = DataManagerFactory('tab')
        td.initialize(example_dir+"D.tab", param="D", format="foo")
        td.open()
        try:
            td.read()
            self.fail("Expected IOError because of bad format")
        except ValueError:
            pass

PyomoTableData = unittest.skipIf(not xls_interface, "No XLS interface available")(PyomoTableData)

class PyomoModelData(unittest.TestCase):

    def test_md1(self):
        md = ModelData()
        md.add(example_dir+"A.tab")
        try:
            md.read()
            self.fail("Must specify a model")
        except ValueError:
            pass
        model=AbstractModel()
        try:
            md.read(model)
            self.fail("Expected ValueError")
        except ValueError:
            pass
        model.A=Set()

    def test_md2(self):
        md = ModelData()
        md.add(currdir+"data1.dat")
        model=AbstractModel()
        model.A=Set()
        md.read(model)

    def test_md3(self):
        md = ModelData()
        md.add(currdir+"data2.dat")
        model=AbstractModel()
        model.A=Set()
        try:
            md.read(model)
            self.fail("Expected error because of extraneous text")
        except IOError:
            pass

    def test_md4(self):
        md = ModelData()
        md.add(currdir+"data3.dat")
        model=AbstractModel()
        model.A=Set()
        model.B=Set()
        model.C=Set()
        md.read(model)

    def test_md5(self):
        md = ModelData()
        md.add(currdir+"data4.dat")
        model=AbstractModel()
        model.A=Set()
        try:
            md.read(model)
        except (ValueError,IOError):
            pass

    def test_md6(self):
        md = ModelData()
        md.add(currdir+"data5.dat")
        model=AbstractModel()
        model.A=Set()
        try:
            md.read(model)
        except ValueError:
            pass

    def test_md7(self):
        md = ModelData()
        md.add(currdir+"data1.tab")
        model=AbstractModel()
        try:
            md.read(model)
            self.fail("Expected IOError")
        except IOError:
            pass

    def test_md8(self):
        md = ModelData()
        md.add(currdir+"data6.dat")
        model=AbstractModel()
        model.A=Set()
        try:
            md.read(model)
            self.fail("Expected IOError")
        except IOError:
            pass

    def test_md9(self):
        md = ModelData()
        md.add(currdir+"data7.dat")
        model=AbstractModel()
        model.A=Set()
        model.B=Param(model.A)
        md.read(model)

    def test_md10(self):
        md = ModelData()
        md.add(currdir+"data8.dat")
        model=AbstractModel()
        model.A=Param(within=Boolean)
        model.B=Param(within=Boolean)
        model.Z=Set()
        md.read(model)
        instance = model.create(md)
        #self.assertEqual(instance.Z.data(), set(['foo[*]' 'bar' '[' '*' ']' 'bar[1,*,a,*]' 'foo-bar' 'hello-goodbye']))

    def test_md11(self):
        cwd = os.getcwd()
        os.chdir(currdir)
        md = ModelData()
        md.add(currdir+"data11.dat")
        model=AbstractModel()
        model.A=Set()
        model.B=Set()
        model.C=Set()
        model.D=Set()
        md.read(model)
        os.chdir(cwd)

    def test_md11(self):
        cwd = os.getcwd()
        os.chdir(currdir)
        model=AbstractModel()
        model.a=Param()
        model.b=Param()
        model.c=Param()
        model.d=Param()
        # Test 1
        instance = model.create(currdir+'data14.dat', namespaces=['ns1','ns2'])
        self.assertEqual( value(instance.a), 1)
        self.assertEqual( value(instance.b), 2)
        self.assertEqual( value(instance.c), 2)
        self.assertEqual( value(instance.d), 2)
        # Test 2
        instance = model.create(currdir+'data14.dat', namespaces=['ns1','ns3','nsX'])
        self.assertEqual( value(instance.a), 1)
        self.assertEqual( value(instance.b), 100)
        self.assertEqual( value(instance.c), 3)
        self.assertEqual( value(instance.d), 100)
        # Test None
        instance = model.create(currdir+'data14.dat')
        self.assertEqual( value(instance.a), -1)
        self.assertEqual( value(instance.b), -2)
        self.assertEqual( value(instance.c), -3)
        self.assertEqual( value(instance.d), -4)
        #
        os.chdir(cwd)


class TestModelData(unittest.TestCase):

    def test_tableA1(self):
        """Importing a single column of data"""
        md = ModelData()
        md.add(os.path.abspath(example_dir+'A.tab'), format='set', set='A')
        model=AbstractModel()
        model.A = Set()
        md.read(model)
        instance = model.create(md)
        self.assertEqual(instance.A.data(), set(['A1', 'A2', 'A3']))

    def test_tableA2(self):
        """Importing a single column of data"""
        md = ModelData()
        md.add(os.path.abspath(example_dir+'A.tab'))
        model=AbstractModel()
        model.A = Set()
        try:
            md.read(model)
            instance = model.create(md)
            self.fail("Should fail because no set name is specified")
        except ValueError:
            pass

    def test_tableA3(self):
        """Importing a single column of data"""
        md = ModelData()
        md.add(os.path.abspath(example_dir+'A.tab'), set='A')
        model=AbstractModel()
        model.A = Set()
        md.read(model)
        instance = model.create(md)

    def test_tableB(self):
        """Same as test_tableA"""
        md = ModelData()
        md.add(os.path.abspath(example_dir+'B.tab'), format='set', set='B')
        model=AbstractModel()
        model.B = Set()
        md.read(model)
        instance = model.create(md)
        self.assertEqual(instance.B.data(), set([1, 2, 3]))

    def test_tableC(self):
        """Importing a multi-column table, where all columns are
        treated as values for a set with tuple values."""
        md = ModelData()
        md.add(os.path.abspath(example_dir+'C.tab'), format='set', set='C')
        model=AbstractModel()
        model.C = Set(dimen=2)
        md.read(model)
        instance = model.create(md)
        self.assertEqual(instance.C.data(), set([('A1',1), ('A1',2), ('A1',3), ('A2',1), ('A2',2), ('A2',3), ('A3',1), ('A3',2), ('A3',3)]))

    def test_tableD(self):
        """Importing a 2D array of data as a set."""
        md = ModelData()
        md.add(os.path.abspath(example_dir+'D.tab'), format='set_array', set='C')
        model=AbstractModel()
        model.C = Set(dimen=2)
        md.read(model)
        instance = model.create(md)
        self.assertEqual(instance.C.data(), set([('A1',1), ('A2',2), ('A3',3)]))

    def test_tableZ(self):
        """Importing a single parameter"""
        md = ModelData()
        md.add(os.path.abspath(example_dir+'Z.tab'), format='param', param='Z')
        model=AbstractModel()
        model.Z = Param(default=99.0)
        md.read(model)
        instance = model.create(md)
        self.assertEqual(instance.Z.value, 1.1)

    def test_tableY(self):
        """Same as tableXW."""
        md = ModelData()
        md.add(os.path.abspath(example_dir+'Y.tab'), index=['A'], param=['Y'])
        model=AbstractModel()
        model.A = Set(initialize=['A1','A2','A3','A4'])
        model.Y = Param(model.A)
        md.read(model)
        instance = model.create(md)
        self.assertEqual(instance.A.data(), set(['A1','A2','A3','A4']))
        self.assertEqual(instance.Y.extract_values(), {'A1':3.3,'A2':3.4,'A3':3.5})

    def test_tableXW_1(self):
        """Importing a table, but only reporting the values for the non-index
        parameter columns.  The first column is assumed to represent an
        index column."""
        md = ModelData()
        md.add(os.path.abspath(example_dir+'XW.tab'), index=['A'], param=['X','W'])
        model=AbstractModel()
        model.A = Set(initialize=['A1','A2','A3','A4'])
        model.X = Param(model.A)
        model.W = Param(model.A)
        md.read(model)
        instance = model.create(md)
        self.assertEqual(instance.A.data(), set(['A1','A2','A3','A4']))
        self.assertEqual(instance.X.extract_values(), {'A1':3.3,'A2':3.4,'A3':3.5})
        self.assertEqual(instance.W.extract_values(), {'A1':4.3,'A2':4.4,'A3':4.5})

    def test_tableXW_2(self):
        """Like test_tableXW_1, except that set A is not defined."""
        md = ModelData()
        md.add(os.path.abspath(example_dir+'XW.tab'), index=['A'], param=['X','W'])
        model=AbstractModel()
        model.A = Set(initialize=['A1','A2','A3'])
        model.X = Param(model.A)
        model.W = Param(model.A)
        md.read(model)
        instance = model.create(md)
        self.assertEqual(instance.X.extract_values(), {'A1':3.3,'A2':3.4,'A3':3.5})
        self.assertEqual(instance.W.extract_values(), {'A1':4.3,'A2':4.4,'A3':4.5})

    def test_tableXW_3(self):
        """Like test_tableXW_1, except that set A is defined in the import statment."""
        md = ModelData()
        md.add(os.path.abspath(example_dir+'XW.tab'), index_name='A', index=['A'], param=['X','W'])
        model=AbstractModel()
        model.A = Set()
        model.X = Param(model.A)
        model.W = Param(model.A)
        md.read(model)
        instance = model.create(md)
        self.assertEqual(instance.A.data(), set(['A1','A2','A3']))
        self.assertEqual(instance.X.extract_values(), {'A1':3.3,'A2':3.4,'A3':3.5})
        self.assertEqual(instance.W.extract_values(), {'A1':4.3,'A2':4.4,'A3':4.5})

    def test_tableXW_4(self):
        """Like test_tableXW_1, except that set A is defined in the import statment and all values are mapped."""
        md = ModelData()
        md.add(os.path.abspath(example_dir+'XW.tab'), index_name='B', index=['A'], param=['X','W'], param_name={'X':'R', 'W':'S'})
        model=AbstractModel()
        model.B = Set()
        model.R = Param(model.B)
        model.S = Param(model.B)
        md.read(model)
        instance = model.create(md)
        self.assertEqual(instance.B.data(), set(['A1','A2','A3']))
        self.assertEqual(instance.R.extract_values(), {'A1':3.3,'A2':3.4,'A3':3.5})
        self.assertEqual(instance.S.extract_values(), {'A1':4.3,'A2':4.4,'A3':4.5})

    def test_tableT(self):
        """Importing a 2D array of parameters that are transposed."""
        md = ModelData()
        md.add(os.path.abspath(example_dir+'T.tab'), format='transposed_array', param='T')
        model=AbstractModel()
        model.B = Set(initialize=['I1','I2','I3','I4'])
        model.A = Set(initialize=['A1','A2','A3'])
        model.T = Param(model.A, model.B)
        md.read(model)
        instance = model.create(md)
        self.assertEqual(instance.T.extract_values(), {('A2', 'I1'): 2.3, ('A1', 'I2'): 1.4, ('A1', 'I3'): 1.5, ('A1', 'I4'): 1.6, ('A1', 'I1'): 1.3, ('A3', 'I4'): 3.6, ('A2', 'I4'): 2.6, ('A3', 'I1'): 3.3, ('A2', 'I3'): 2.5, ('A3', 'I2'): 3.4, ('A2', 'I2'): 2.4, ('A3', 'I3'): 3.5})

    def test_tableU(self):
        """Importing a 2D array of parameters."""
        md = ModelData()
        md.add(os.path.abspath(example_dir+'T.tab'), format='array', param='U')
        model=AbstractModel()
        model.A = Set(initialize=['I1','I2','I3','I4'])
        model.B = Set(initialize=['A1','A2','A3'])
        model.U = Param(model.A, model.B)
        md.read(model)
        instance = model.create(md)
        self.assertEqual(instance.U.extract_values(), {('I2', 'A1'): 1.4, ('I3', 'A1'): 1.5, ('I3', 'A2'): 2.5, ('I4', 'A1'): 1.6, ('I3', 'A3'): 3.5, ('I1', 'A2'): 2.3, ('I4', 'A3'): 3.6, ('I1', 'A3'): 3.3, ('I4', 'A2'): 2.6, ('I2', 'A3'): 3.4, ('I1', 'A1'): 1.3, ('I2', 'A2'): 2.4})

    def test_tableS(self):
        """Importing a table, but only reporting the values for the non-index
        parameter columns.  The first column is assumed to represent an
        index column.  A missing value is represented in the column data."""
        md = ModelData()
        md.add(os.path.abspath(example_dir+'S.tab'), index=['A'], param=['S'])
        model=AbstractModel()
        model.A = Set(initialize=['A1','A2','A3','A4'])
        model.S = Param(model.A)
        md.read(model)
        instance = model.create(md)
        self.assertEqual(instance.A.data(), set(['A1','A2','A3','A4']))
        self.assertEqual(instance.S.extract_values(), {'A1':3.3,'A3':3.5})

    def test_tablePO(self):
        """Importing a table that has multiple indexing columns"""
        pyutilib.misc.setup_redirect(currdir+'importPO.dat')
        print("import "+os.path.abspath(example_dir+'PO.tab')+" : J=[A,B] P O;")
        pyutilib.misc.reset_redirect()
        md = ModelData()
        md.add(os.path.abspath(example_dir+'PO.tab'), index_name='J', index=['A','B'], param=['P','O'])
        model=AbstractModel()
        model.J = Set(dimen=2)
        model.P = Param(model.J)
        model.O = Param(model.J)
        md.read(model)
        instance = model.create(md)
        self.assertEqual(instance.J.data(), set([('A3', 'B3'), ('A1', 'B1'), ('A2', 'B2')]) )
        self.assertEqual(
            instance.P.extract_values(),
            {('A3', 'B3'): 4.5, ('A1', 'B1'): 4.3, ('A2', 'B2'): 4.4} )
        self.assertEqual(instance.O.extract_values(), {('A3', 'B3'): 5.5, ('A1', 'B1'): 5.3, ('A2', 'B2'): 5.4})


if __name__ == "__main__":
    unittest.main()
