# SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: LicenseRef-NvidiaProprietary
#
# NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
# property and proprietary rights in and to this material, related
# documentation and any modifications thereto. Any use, reproduction,
# disclosure or distribution of this material and related documentation
# without an express license agreement from NVIDIA CORPORATION or
# its affiliates is strictly prohibited.

from pathlib import Path
from pydantic import BaseModel, Field

import omni.kit.commands
import omni.usd
from omni.services.core.routers import ServiceAPIRouter

from pxr import Gf, Sdf, UsdGeom, UsdShade

router = ServiceAPIRouter(tags=["My Service Setup Extension"])


class CubeDataModel(BaseModel):
    """Model of a request for generating a cube."""

    asset_write_location: str = Field(
        default="/asset_write_path",
        title="Asset Path",
        description="Location on device to write generated asset",
    )

    asset_name: str = Field(
        default="cube",
        title="Asset Name",
        description="Name of the asset to be generated, .usda will be appended to the name",
    )

    cube_scale: float = Field(
        default=100,
        title="Cube Scale",
        description="Scale of the cube",
    )

class SceneDataModel(BaseModel):
    """Model of a request for generating a scene of primitives."""

    asset_write_location: str = Field(
        default="/asset_write_path",
        title="Asset Path",
        description="Location on device to write generated asset",
    )

    asset_name: str = Field(
        default="scene",
        title="Asset Name",
        description="Name of the asset to be generated, .usda will be appended to the name",
    )

    num_cubes: int = Field(
        default=5,
        ge=1,
        le=20,
        title="Number of Cubes",
        description="Number of cubes to create",
    )

    cube_spacing: float = Field(
        default=50,
        ge=1,
        le=100,
        title="Cube Spacing",
        description="Distance between each cube",
    )

    cube_scale: float = Field(
        default=10,
        ge=1,
        le=100,
        title="Cube Scale",
        description="Scale of the cubes",
    )

    num_spheres: int = Field(
        default=4,
        ge=1,
        le=20,
        title="Number of Spheres",
        description="Number of spheres to create",
    )

    sphere_spacing: float = Field(
        default=20,
        ge=1,
        le=100,
        title="Sphere Spacing",
        description="Distance between each sphere",
    )

    sphere_scale: float = Field(
        default=8,
        ge=1,
        le=100,
        title="Sphere Scale",
        description="Scale of the spheres",
    )

    ground_plane_scale: float = Field(
        default=40,
        ge=1,
        le=100,
        title="Ground Plane Scale",
        description="Scale of the ground plane",
    )

def create_prims(stage, prim_type: str, quantity: int, spacing: float, prim_scale: float):

    # Offset Cubes and Spheres
    if prim_type == "Cube":
        start = (prim_scale * 2, prim_scale, 0)
    else:  # if prim_type == "Sphere":
        start = (-prim_scale * 2, prim_scale, 0)

    for i in range(quantity):
        prim_path = omni.usd.get_stage_next_free_path(
            stage,
            f"/World/{prim_type}",
            False
        )

        omni.kit.commands.execute(
            "CreatePrimCommand",
            prim_path=prim_path,
            prim_type=prim_type,
            select_new_prim=False,
        )

        translation = (start[0], start[1], start[2] + (i * spacing))
        scale = (prim_scale, prim_scale, prim_scale)
        omni.kit.commands.execute(
            "TransformPrimSRT",
            path=prim_path,
            new_translation=translation,
            new_scale=scale,
        )


def create_ground_plane(stage, plane_scale: float):
    prim_type = "Plane"
    prim_path = f"/World/{prim_type}"

    omni.kit.commands.execute(
        "CreateMeshPrim",
        prim_path=prim_path,
        prim_type=prim_type,
        select_new_prim=False,
    )

    prim = stage.GetPrimAtPath(prim_path)
    xform = UsdGeom.Xformable(prim)
    xform_ops = {op.GetBaseName(): op for op in xform.GetOrderedXformOps()}
    scale = xform_ops["scale"]
    scale.Set(Gf.Vec3d(plane_scale, 1, plane_scale))


def apply_material(stage):
    prim = stage.GetPrimAtPath('/World/Sphere')
    materials_path = "/World/Looks"
    material_path = f"{materials_path}/OmniPBR"

    omni.kit.commands.execute('CreatePrim',
        prim_path=materials_path,
        prim_type="Scope",
        select_new_prim=False,
    )

    omni.kit.commands.execute('CreateMdlMaterialPrim',
        mtl_url="OmniPBR.mdl",
        mtl_name="OmniPBR",
        mtl_path=material_path,
        select_new_prim=True,
    )


    custom_shader = UsdShade.Shader(stage.GetPrimAtPath(f"{material_path}/Shader"))
    custom_shader.CreateInput("diffuse_color_constant", Sdf.ValueTypeNames.Color3f).Set(Gf.Vec3f(.46, .73, 0))
    custom_shader.CreateInput("reflection_roughness_constant", Sdf.ValueTypeNames.Float).Set(.25)

    omni.kit.commands.execute(
        "BindMaterial",
        prim_path=prim.GetPrimPath(),
        material_path=material_path
    )

@router.post(
    "/generate_cube",
    summary="Generate a cube",
    description="An endpoint to generate a usda file containing a cube of given scale",
)
async def generate_cube(cube_data: CubeDataModel):
    print("[my_company.my_service_setup_extension] generate_cube was called")

    # Create a new stage
    usd_context = omni.usd.get_context()
    usd_context.new_stage()
    stage = omni.usd.get_context().get_stage()

    # Set the default prim
    default_prim_path = "/World"
    stage.DefinePrim(default_prim_path, "Xform")
    prim = stage.GetPrimAtPath(default_prim_path)
    stage.SetDefaultPrim(prim)

    # Create cube
    prim_type = "Cube"
    prim_path = f"/World/{prim_type}"

    omni.kit.commands.execute(
        "CreatePrim",
        prim_path=prim_path,
        prim_type=prim_type,
        attributes={"size": cube_data.cube_scale},
        select_new_prim=False,
    )

    # save stage
    asset_file_path = str(Path(
        cube_data.asset_write_location).joinpath(f"{cube_data.asset_name}.usda")
    )
    stage.GetRootLayer().Export(asset_file_path)
    msg = f"[my_company.my_service_setup_extension] Wrote a cube to this path: {asset_file_path}"
    print(msg)
    return msg

@router.post(
    "/generate_scene",
    summary="Generate a scene of primitives",
    description="An endpoint to generate a usda file containing cubes, spheres and a groundplane.",
)
async def generate_scene(scene_data: SceneDataModel):
    print("tutorial.service.setup generate_scene was called")

    # Create a new stage
    usd_context = omni.usd.get_context()
    usd_context.new_stage()
    stage = omni.usd.get_context().get_stage()

    # Set the default prim
    default_prim_path = "/World"
    stage.DefinePrim(default_prim_path, "Xform")
    prim = stage.GetPrimAtPath(default_prim_path)
    stage.SetDefaultPrim(prim)

    # Create Cubes
    create_prims(
        stage,
        "Cube",
        scene_data.num_cubes,
        scene_data.cube_spacing,
        scene_data.cube_scale,
    )
    # Create Spheres
    create_prims(
        stage,
        "Sphere",
        scene_data.num_spheres,
        scene_data.sphere_spacing,
        scene_data.sphere_scale,
    )

    # Create a Ground Plane
    create_ground_plane(
        stage,
        scene_data.ground_plane_scale)

    # Apply a material to a Sphere
    apply_material(stage)

    # save stage
    asset_file_path = str(Path(scene_data.asset_write_location).joinpath(f"{scene_data.asset_name}.usda"))
    stage.GetRootLayer().Export(asset_file_path)
    msg = f"tutorial.service.setup Wrote a scene to this path: {asset_file_path}"
    print(msg)
    return msg