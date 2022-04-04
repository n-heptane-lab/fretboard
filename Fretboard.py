# Assuming you have not changed the general structure of the template no modification is needed in this file.
from . import commands
from .lib import fusion360utils as futil
import adsk.core, adsk.fusion, adsk.cam, traceback, math

handlers = []

def fretPosition(fretNumber, scaleLength):
    return (scaleLength / (2 ** (fretNumber / 12))) - scaleLength
    #return (scaleLength - (scaleLength / (2 ^ (fretNumber / 12))))

#
def drawFrets(sketch, numFrets, scaleLength):
    #sketchNACA = rootComp.sketches.add(rootComp.xYConstructionPlane)
    #app = adsk.core.Application.get()

    sketch.isDeferred = True

    #fret_points = adsk.core.ObjectCollection.create()

    sketchLines = sketch.sketchCurves.sketchLines

    startPoint = adsk.core.Point3D.create(0, 0, 0)
    for n in range(1, 1 + numFrets):
        endPoint = adsk.core.Point3D.create(0, fretPosition(n, scaleLength), 0)
        sketchLines.addByTwoPoints(startPoint, endPoint)
        startPoint = endPoint
    
    sketchLines.addByTwoPoints(startPoint, adsk.core.Point3D.create(0, -scaleLength, 0))
    #naca_spline = sketch.sketchCurves.sketchFittedSplines.add(naca_points)

    sketch.isDeferred = False

# Event handler for the execute event.
class FretboardCommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        eventArgs = adsk.core.CommandEventArgs.cast(args)

        app = adsk.core.Application.get()
        ui  = app.userInterface

        # Get the values from the command inputs.
        inputs = eventArgs.command.commandInputs

        numFrets  = inputs.itemById("numFrets").value
        scaleLength = inputs.itemById("scaleLength").value

        #ui.messageBox(str(chord))

        sketch = adsk.fusion.Sketch.cast(app.activeEditObject)

        drawFrets(sketch, numFrets, scaleLength)

# Event handler for the commandCreated event.
class FretboardCommandCreatedEventHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        # Verify that a sketch is active. Why here and not Execute?
        app = adsk.core.Application.get()
        if app.activeEditObject.objectType != adsk.fusion.Sketch.classType():
            ui = app.userInterface
            ui.messageBox('A sketch must be active for this command.')
            return False

        eventArgs = adsk.core.CommandCreatedEventArgs.cast(args)

        # Get the command
        cmd = eventArgs.command

        # Get the commandInputs collection to create new command inputs.
        inputs = cmd.commandInputs

        # create things
        #app.userInterface.messageBox('get inputs')

        numFrets  = inputs.addIntegerSpinnerCommandInput('numFrets', "Num Frets", 1, 36, 1, 21)
        scaleLength = inputs.addFloatSpinnerCommandInput('scaleLength', 'Scale Length', 'in', 0, 100, 1, 25.5   )
        #chord     = inputs.addValueInput ('chord', "Chord", app.activeProduct.design.unitsManager.defaultLengthUnits, 10)
        #chord     = inputs.addValueInput ('chord', "Chord", "cm", adsk.core.ValueInput.createByReal(10.0))
        #app.userInterface.messageBox(app.activeProduct.unitsManager.defaultLengthUnits)
        #app.userInterface.messageBox("added three inputs")

        # Connect to the execute event.
        onExecute = FretboardCommandExecuteHandler()
        cmd.execute.add(onExecute)
        handlers.append(onExecute)


def run(context):
    ui = None
    try:
        # This will run the start function in each of your commands as defined in commands/__init__.py
        commands.start()
        app = adsk.core.Application.get()

        # Get the UserInterface object and the CommandDefinitions collection.
        ui  = app.userInterface
        cmdDefs = ui.commandDefinitions

        # Create a button command definition.
        buttonFretboard = cmdDefs.addButtonDefinition('FretboardButtonDefId', 'Fretboard',
                                            'Create a fretboard',
                                            './/Resources//Fretboard')

        # Connect to the command created event.
        buttonFretboardCreated = FretboardCommandCreatedEventHandler()
        buttonFretboard.commandCreated.add(buttonFretboardCreated)
        handlers.append(buttonFretboardCreated)

        # Get the ADD-INS panel in the model workspace.
        sketchPanel = ui.allToolbarPanels.itemById('SketchPanel')

        # Add the buttons to the bottom of the panel.
        buttonFretboardControl    = sketchPanel.controls.addCommand(buttonFretboard)
    except:
        futil.handle_error('run')


def stop(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface

        #ui.messageBox('stop')
        # Clean up the UI.
        cmdDef = ui.commandDefinitions.itemById('FretboardButtonDefId')
        if cmdDef:
            #ui.messageBox('cmdDef.deleteMe')
            cmdDef.deleteMe()

        sketchPanel = ui.allToolbarPanels.itemById('SketchPanel')
        cntrl = sketchPanel.controls.itemById('FretboardButtonDefId')
        if cntrl:
            #ui.messageBox('cntrl.deleteMe')
            cntrl.deleteMe()

        # Remove all of the event handlers your app has created
        futil.clear_handlers()

        # This will run the start function in each of your commands as defined in commands/__init__.py
        commands.stop()

    except:
        futil.handle_error('stop')