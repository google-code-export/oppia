from core.domain import widget_domain

class ChessInput(widget_domain.BaseWidget):
    """Interactive widget for entering chess positions"""

    # The human-readable name of the widget.
    name = 'Chess'

    # The category the widget falls under in the widget repository.
    category = 'Custom'

    # A description of the widget.
    description = (
        'A chess input widget that provides a movable board.'
    )

    # Customization args and their descriptions, schemas and default
    # values.
    # NB: There used to be an integer-typed parameter here called 'columns'
    # that was removed in revision 628942010573. Some text widgets in
    # older explorations may have this customization parameter still set
    # in the exploration definition, so, in order to minimize the possibility
    # of collisions, do not add a new parameter with this name to this list.
    # TODO(sll): Migrate old definitions which still contain the 'columns'
    # parameter.
    _customization_arg_specs = [{
        'name': 'chess',
        'description': 'Editor for the chess position you want to show the student',
        'schema': {
            'type': 'custom',
            'obj_type': 'Chess',
        },
        'default_value': 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR'
    }]

    # Actions that the reader can perform on this widget which trigger a
    # feedback interaction, and the associated input types. Interactive widgets
    # must have at least one of these. This attribute name MUST be prefixed by
    # '_'.
    _handlers = [{
        'name': 'submit', 'obj_type': 'Chess'
    }]

    # Additional JS library dependencies that should be loaded in pages
    # containing this widget. These should correspond to names of files in
    # feconf.DEPENDENCIES_TEMPLATES_DIR.
    _dependency_ids = ['chessboard']
