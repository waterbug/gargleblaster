# -*- mode: python -*-

block_cipher = None

import os
import pangalactic.core.ontology
import pangalactic.core.test.data
import pangalactic.core.test.vault
import OCC
onto_mod_path = pangalactic.core.ontology.__path__[0]
onto_paths = [(os.path.join(onto_mod_path, p),
               os.path.join('pangalactic', 'core', 'ontology'))
              for p in os.listdir(onto_mod_path)
              if not p.startswith('__init__')]
data_mod_path = pangalactic.core.test.data.__path__[0]
data_paths = [(os.path.join(data_mod_path, p),
               os.path.join('pangalactic', 'core', 'test', 'data'))
              for p in os.listdir(data_mod_path)
              if not p.startswith('__init__')]
vault_mod_path = pangalactic.core.test.vault.__path__[0]
vault_paths = [(os.path.join(vault_mod_path, p),
                'pangalactic/core/test/vault')
               for p in os.listdir(vault_mod_path)
               if not p.startswith('__init__')]

import pangalactic.node.icons
import pangalactic.node.images
icon_mod_path = pangalactic.node.icons.__path__[0]
icon_paths = [(os.path.join(icon_mod_path, p),
               'pangalactic/node/icons')
              for p in os.listdir(icon_mod_path)
              if not p.startswith('__init__')]
image_mod_path = pangalactic.node.images.__path__[0]
image_paths = [(os.path.join(image_mod_path, p),
                'pangalactic/node/images')
               for p in os.listdir(image_mod_path)
               if not p.startswith('__init__')]
occ_pkg_path = os.path.dirname(OCC.__file__)
casroot = os.path.join(occ_pkg_path, '..', '..', '..', '..',
                       'share', 'opencascade')
casroot_paths = [(casroot, os.path.join('gargleblaster', 'casroot'))]
platforms = os.path.join(occ_pkg_path, '..', '..', '..', '..',
                         'plugins', 'platforms')
platforms_paths = [(platforms, 'platforms')]

data_files = [('test/data', 'gargleblaster/test/data'),
              ('../doc', 'gargleblaster/doc'),
             ]
data_files += onto_paths
data_files += data_paths
data_files += vault_paths
data_files += icon_paths
data_files += image_paths
data_files += casroot_paths
data_files += platforms_paths

a = Analysis(['__main__.py'],
             pathex=['/Users/waterbug/clones/gargleblaster/gargleblaster'],
             binaries=[],
             datas=data_files,
             hiddenimports=['_sysconfigdata', 'pangalactic.core',
             'pangalactic.core.ontology', 'pangalactic.node',
             'pangalactic.node.pangalaxian', 'sqlalchemy.ext.baked',
             'sip', 'PyQt5', 'PyQt5.QtCore', 'PyQt5.QtGui',
             'PyQt5.QtWidgets', 'OCC.Adaptor2d', 'OCC.BRepSweep',
             'OCC.GeomLProp', 'OCC.MAT', 'OCC.StepGeom', 'OCC.Adaptor3d',
             'OCC.BRepTools', 'OCC.GeomPlate', 'OCC.MeshVS', 'OCC.StepRepr',
             'OCC.AdvApp2Var', 'OCC.BRepTopAdaptor', 'OCC.GeomProjLib',
             'OCC.Message', 'OCC.STEPSelections', 'OCC.AdvApprox',
             'OCC.BSplCLib', 'OCC.Geom', 'OCC.MMgt', 'OCC.StepShape',
             'OCC.AIS', 'OCC.BSplSLib', 'OCC.GeomTools', 'OCC.NCollection',
             'OCC.StepToGeom', 'OCC.AppBlend', 'OCC.ChFi2d', 'OCC.GeomToStep',
             'OCC.NLPlate', 'OCC.StepToTopoDS', 'OCC.AppCont', 'OCC.ChFi3d',
             'OCC.gp', 'OCC.OSD', 'OCC.StlAPI', 'OCC.AppDef', 'OCC.ChFiDS',
             'OCC.GProp', 'OCC.Plate', 'OCC.StlMesh', 'OCC.AppParCurves',
             'OCC.ChFiKPart', 'OCC.GraphDS', 'OCC.PLib', 'OCC.StlTransfer',
             'OCC.ApproxInt', 'OCC.Contap', 'OCC.Graphic3d', 'OCC.Plugin',
             'OCC.Storage', 'OCC.Approx', 'OCC.Convert', 'OCC.GraphTools',
             'OCC.Poly', 'OCC.Sweep', 'OCC.AppStdL', 'OCC.CPnts',
             'OCC.HatchGen', 'OCC.Precision', 'OCC.TColGeom2d', 'OCC.AppStd',
             'OCC.CSLib', 'OCC.Hatch', 'OCC.Primitives', 'OCC.TColGeom',
             'OCC.Aspect', 'OCC.Dico', 'OCC.Hermit', 'OCC.ProjLib',
             'OCC.TColgp', 'OCC.Bisector', 'OCC.Draft', 'OCC.HLRAlgo',
             'OCC.Prs3d', 'OCC.TCollection', 'OCC.BiTgte', 'OCC.DsgPrs',
             'OCC.HLRAppli', 'OCC.PrsMgr', 'OCC.TColQuantity', 'OCC.BlendFunc',
             'OCC.Dynamic', 'OCC.HLRBRep', 'OCC.Quantity', 'OCC.TColStd',
             'OCC.Blend', 'OCC.ElCLib', 'OCC.HLRTopoBRep', 'OCC.Resource',
             'OCC.TDataStd', 'OCC.BndLib', 'OCC.ElSLib', 'OCC.IFSelect',
             'OCC.RWStepAP203', 'OCC.TDataXtd', 'OCC.Bnd', 'OCC.ExprIntrp',
             'OCC.IGESCAFControl', 'OCC.RWStepAP214', 'OCC.TDF', 'OCC.BOPAlgo',
             'OCC.Expr', 'OCC.IGESControl', 'OCC.RWStepBasic', 'OCC.TDocStd',
             'OCC.BOPCol', 'OCC.Extrema', 'OCC.Image', 'OCC.RWStepGeom',
             'OCC.TFunction', 'OCC.BOPDS', 'OCC.FairCurve',
             'OCC.IncludeLibrary', 'OCC.RWStepRepr', 'OCC.TNaming',
             'OCC.BOPInt', 'OCC.FEmTool', 'OCC.RWStepShape',
             'OCC.TopAbs', 'OCC.BOPTools', 'OCC.FilletSurf', 'OCC.IntAna2d',
             'OCC.RWStl', 'OCC.TopBas', 'OCC.BRepAdaptor', 'OCC.FSD',
             'OCC.IntAna', 'OCC.Select3D', 'OCC.TopClass', 'OCC.BRepAlgoAPI',
             'OCC.IntCurve', 'OCC.SelectBasics',
             'OCC.TopCnx', 'OCC.BRepAlgo', 'OCC.GccAna', 'OCC.IntCurvesFace',
             'OCC.SelectMgr', 'OCC.TopExp', 'OCC.BRepApprox', 'OCC.GccEnt',
             'OCC.IntCurveSurface', 'OCC.ShapeAlgo', 'OCC.TopLoc',
             'OCC.BRepBlend', 'OCC.GccGeo', 'OCC.InterfaceGraphic',
             'OCC.ShapeAnalysis', 'OCC.TopoDS', 'OCC.BRepBndLib', 'OCC.GccInt',
             'OCC.Interface', 'OCC.ShapeBuild', 'OCC.TopoDSToStep',
             'OCC.BRepBuilderAPI', 'OCC.GccIter', 'OCC.Intf',
             'OCC.ShapeConstruct', 'OCC.TopOpeBRepBuild', 'OCC.BRepCheck',
             'OCC.GCE2d', 'OCC.IntImpParGen', 'OCC.ShapeCustom',
             'OCC.TopOpeBRepDS', 'OCC.BRepClass3d', 'OCC.gce', 'OCC.IntImp',
             'OCC.ShapeExtend', 'OCC.TopOpeBRep', 'OCC.BRepClass',
             'OCC.GCPnts', 'OCC.IntPatch', 'OCC.ShapeFix',
             'OCC.TopOpeBRepTool', 'OCC.BRepExtrema', 'OCC.GC', 'OCC.IntPolyh',
             'OCC.ShapeProcessAPI', 'OCC.TopTools', 'OCC.BRepFeat',
             'OCC.Geom2dAdaptor', 'OCC.IntPoly', 'OCC.ShapeProcess',
             'OCC.TopTrans', 'OCC.BRepFilletAPI', 'OCC.Geom2dAPI',
             'OCC.IntRes2d', 'OCC.ShapeUpgrade', 'OCC.TPrsStd', 'OCC.BRepFill',
             'OCC.Geom2dConvert', 'OCC.Intrv', 'OCC.SortTools', 'OCC.TShort',
             'OCC.BRepGProp', 'OCC.Geom2dGcc', 'OCC.IntStart', 'OCC.Standard',
             'OCC.UnitsAPI', 'OCC.BRepIntCurveSurface', 'OCC.Geom2dHatch',
             'OCC.IntSurf', 'OCC.StdFail', 'OCC.Units', 'OCC.BRepLib',
             'OCC.Geom2dInt', 'OCC.IntTools', 'OCC.StdPrs', 'OCC.V3d',
             'OCC.BRepLProp', 'OCC.Geom2dLProp', 'OCC.IntWalk',
             'OCC.StdSelect', 'OCC.Visual3d', 'OCC.BRepMAT2d', 'OCC.Geom2d',
             'OCC.Law', 'OCC.StepAP203', 'OCC.Visualization', 'OCC.BRepMesh',
             'OCC.GeomAbs', 'OCC.LocalAnalysis', 'OCC.StepAP209',
             'OCC.XBRepMesh', 'OCC.BRepOffsetAPI', 'OCC.GeomAdaptor',
             'OCC.LocOpe', 'OCC.StepAP214', 'OCC.XCAFApp', 'OCC.BRepOffset',
             'OCC.GeomAPI', 'OCC.LProp3d', 'OCC.StepBasic', 'OCC.XCAFDoc',
             'OCC.BRepPrimAPI', 'OCC.GeomConvert', 'OCC.LProp',
             'OCC.STEPCAFControl', 'OCC.XCAFPrs', 'OCC.BRepPrim',
             'OCC.GeomFill', 'OCC.MAT2d', 'OCC.STEPConstruct', 'OCC.XSControl',
             'OCC.BRepProj', 'OCC.GeomInt', 'OCC.Materials', 'OCC.STEPControl',
             'OCC.BRep', 'OCC.GeomLib', 'OCC.math', 'OCC.STEPEdit',
             'rdflib.plugins.memory', 'rdflib.plugins.parsers.rdfxml'],
             # 'OCC.GarbageCollector' not found, removed from hidden imports
             hookspath=[],
             runtime_hooks=[],
             excludes=['docutils', 'FixTk', 'tcl', 'tk', '_tkinter', 'tkinter',
                'Tkinter', 'pyqt4', 'PySide', 'IPython', 'ipython', 'pdb',
                'sphinx', 'zmq'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
          cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='run_gargleblaster',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='garg')

