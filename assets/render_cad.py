from pathlib import Path

from vtkmodules.vtkIOGeometry import vtkSTLReader
from vtkmodules.vtkIOImage import vtkPNGWriter
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkCamera,
    vtkLight,
    vtkPolyDataMapper,
    vtkRenderer,
    vtkRenderWindow,
    vtkWindowToImageFilter,
)
import vtkmodules.vtkRenderingOpenGL2  # noqa: F401


ROOT = Path(__file__).resolve().parents[1]
EXPORTS = ROOT / "cad" / "exports"
OUTPUT = ROOT / "assets" / "tool-tracker-v2-render.png"


def add_part(renderer, filename, color, position, roughness=0.65):
    reader = vtkSTLReader()
    reader.SetFileName(str(EXPORTS / filename))

    mapper = vtkPolyDataMapper()
    mapper.SetInputConnection(reader.GetOutputPort())

    actor = vtkActor()
    actor.SetMapper(mapper)
    actor.SetPosition(*position)
    actor.GetProperty().SetColor(*color)
    actor.GetProperty().SetRoughness(roughness)
    actor.GetProperty().SetMetallic(0.05)
    renderer.AddActor(actor)
    return actor


def main():
    renderer = vtkRenderer()
    renderer.SetBackground(0.93, 0.94, 0.92)

    # Two tool modules, slightly separated.
    add_part(
        renderer,
        "tool_tile_base.stl",
        (0.10, 0.12, 0.14),
        (-48, -36, 0),
    )
    add_part(
        renderer,
        "tool_tile_top_choc.stl",
        (0.27, 0.31, 0.34),
        (-48, -36, 16),
    )
    add_part(
        renderer,
        "preview_tile_switches.stl",
        (0.93, 0.62, 0.12),
        (-48, -36, 19),
    )

    add_part(
        renderer,
        "tool_tile_base.stl",
        (0.10, 0.12, 0.14),
        (-48, 36, 0),
    )
    add_part(
        renderer,
        "tool_tile_top_choc.stl",
        (0.27, 0.31, 0.34),
        (-48, 36, 16),
    )
    add_part(
        renderer,
        "preview_tile_switches.stl",
        (0.20, 0.67, 0.53),
        (-48, 36, 19),
    )

    # Keypad hub beside the tool tiles.
    add_part(
        renderer,
        "keypad_hub_base.stl",
        (0.09, 0.11, 0.13),
        (92, 0, 0),
    )
    add_part(
        renderer,
        "keypad_hub_top.stl",
        (0.32, 0.36, 0.39),
        (92, 0, 20),
    )
    add_part(
        renderer,
        "preview_keypad_keys.stl",
        (0.92, 0.62, 0.12),
        (92, 0, 23),
    )
    add_part(
        renderer,
        "preview_display.stl",
        (0.05, 0.30, 0.24),
        (92, 0, 23),
        roughness=0.3,
    )

    key = vtkLight()
    key.SetPosition(250, -250, 320)
    key.SetFocalPoint(0, 0, 0)
    key.SetIntensity(0.9)
    renderer.AddLight(key)

    fill = vtkLight()
    fill.SetPosition(-250, 150, 180)
    fill.SetFocalPoint(0, 0, 0)
    fill.SetIntensity(0.55)
    renderer.AddLight(fill)

    camera = vtkCamera()
    camera.SetPosition(330, -360, 285)
    camera.SetFocalPoint(15, 0, 8)
    camera.SetViewUp(0, 0, 1)
    renderer.SetActiveCamera(camera)
    renderer.ResetCamera()
    camera.Dolly(1.25)
    renderer.ResetCameraClippingRange()

    window = vtkRenderWindow()
    window.SetOffScreenRendering(1)
    window.SetSize(1600, 1000)
    window.AddRenderer(renderer)
    window.Render()

    capture = vtkWindowToImageFilter()
    capture.SetInput(window)
    capture.SetScale(1)
    capture.SetInputBufferTypeToRGBA()
    capture.ReadFrontBufferOff()
    capture.Update()

    writer = vtkPNGWriter()
    writer.SetFileName(str(OUTPUT))
    writer.SetInputConnection(capture.GetOutputPort())
    writer.Write()
    print("Render written to", OUTPUT)


if __name__ == "__main__":
    main()
