##########################################################################
#
#  Copyright (c) 2017, Image Engine Design Inc. All rights reserved.
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are
#  met:
#
#      * Redistributions of source code must retain the above
#        copyright notice, this list of conditions and the following
#        disclaimer.
#
#      * Redistributions in binary form must reproduce the above
#        copyright notice, this list of conditions and the following
#        disclaimer in the documentation and/or other materials provided with
#        the distribution.
#
#      * Neither the name of Image Engine Design Inc nor the names of
#        any other contributors to this software may be used to endorse or
#        promote products derived from this software without specific prior
#        written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
#  IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
#  THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
#  PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
#  CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
#  EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
#  PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
#  PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
#  LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
#  NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#  SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
##########################################################################

import os
import imath

import IECore
import IECoreScene
import IECoreVDB

import GafferTest
import GafferScene
import GafferVDB
import GafferVDBTest

class LevelSetToMeshTest( GafferVDBTest.VDBTestCase ) :

	def setUp( self ) :
		GafferVDBTest.VDBTestCase.setUp( self )
		self.sourcePath = os.path.join( self.dataDir, "sphere.vdb" )
		self.sceneInterface = IECoreScene.SceneInterface.create( self.sourcePath, IECore.IndexedIO.OpenMode.Read )

	def testCanConvertLevelSetToMesh( self ) :
		sphere = GafferScene.Sphere()
		meshToLevelSet = GafferVDB.MeshToLevelSet()
		self.setFilter( meshToLevelSet, path='/sphere' )
		meshToLevelSet["voxelSize"].setValue( 0.05 )
		meshToLevelSet["in"].setInput( sphere["out"] )

		obj = meshToLevelSet["out"].object( "sphere" )

		self.assertTrue( isinstance( obj, IECoreVDB.VDBObject ) )

		self.assertEqual( obj.gridNames(), ['surface'] )
		grid = obj.findGrid( "surface" )

		levelSetToMesh = GafferVDB.LevelSetToMesh()
		self.setFilter( levelSetToMesh, path='/sphere' )
		levelSetToMesh["in"].setInput( meshToLevelSet["out"] )

		mesh = levelSetToMesh["out"].object( "sphere" )
		self.assertTrue( isinstance( mesh, IECoreScene.MeshPrimitive) )

	def testChangingIsoValueUpdatesBounds ( self ) :
		sphere = GafferScene.Sphere()
		sphere["radius"].setValue( 5 )

		meshToLevelSet = GafferVDB.MeshToLevelSet()
		self.setFilter( meshToLevelSet, path='/sphere' )
		meshToLevelSet["voxelSize"].setValue( 0.05 )
		meshToLevelSet["exteriorBandwidth"].setValue( 4.0 )
		meshToLevelSet["interiorBandwidth"].setValue( 4.0 )
		meshToLevelSet["in"].setInput( sphere["out"] )

		levelSetToMesh = GafferVDB.LevelSetToMesh()
		self.setFilter( levelSetToMesh, path='/sphere' )
		levelSetToMesh["in"].setInput( meshToLevelSet["out"] )

		self.assertEqualTolerance( 5.0, levelSetToMesh['out'].bound( "sphere" ).max()[0], 0.05 )

		levelSetToMesh['isoValue'].setValue(0.5)
		self.assertEqualTolerance( 5.5, levelSetToMesh['out'].bound( "sphere" ).max()[0], 0.05 )

		levelSetToMesh['isoValue'].setValue(-0.5)
		self.assertEqualTolerance( 4.5, levelSetToMesh['out'].bound( "sphere" ).max()[0], 0.05 )

	def testIncreasingAdapativityDecreasesPolyCount( self ) :
		sphere = GafferScene.Sphere()
		sphere["radius"].setValue( 5 )

		meshToLevelSet = GafferVDB.MeshToLevelSet()
		self.setFilter( meshToLevelSet, path='/sphere' )
		meshToLevelSet["voxelSize"].setValue( 0.05 )
		meshToLevelSet["exteriorBandwidth"].setValue( 4.0 )
		meshToLevelSet["interiorBandwidth"].setValue( 4.0 )
		meshToLevelSet["in"].setInput( sphere["out"] )

		levelSetToMesh = GafferVDB.LevelSetToMesh()
		self.setFilter( levelSetToMesh, path='/sphere')
		levelSetToMesh["in"].setInput( meshToLevelSet["out"] )

		levelSetToMesh['adaptivity'].setValue(0.0)
		self.assertTrue( 187000 <=  len( levelSetToMesh['out'].object( "sphere" ).verticesPerFace ) <= 188000 )

		levelSetToMesh['adaptivity'].setValue(1.0)
		self.assertTrue( 2800 <= len( levelSetToMesh['out'].object( "sphere" ).verticesPerFace ) <= 3200 )
