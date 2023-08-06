from collections import OrderedDict
from jinja2 import Template
import md5
import sys

class OrderedDefaultdict(OrderedDict):
    def __init__(self, *args, **kwargs):
        newdefault = None
        newargs = ()
        if args:
            newdefault = args[0]
            if not (newdefault is None or callable(newdefault)):
                raise TypeError('first argument must be callable or None')
            newargs = args[1:]
        self.default_factory = newdefault
        super(self.__class__, self).__init__(*newargs, **kwargs)

    def __missing__ (self, key):
        if self.default_factory is None:
            raise KeyError(key)
        self[key] = value = self.default_factory()
        return value

    def __reduce__(self):  # optional, for pickle support
        args = self.default_factory if self.default_factory else tuple()
        return type(self), args, None, None, self.items()

command_template_table = """
<html>
<head>
    <title></title>
    <link href="http://twitter.github.com/bootstrap/assets/css/bootstrap.css" rel="stylesheet">
    <link href="http://twitter.github.com/bootstrap/assets/css/docs.css" rel="stylesheet">
    <link href="http://twitter.github.com/bootstrap/assets/css/bootstrap-responsive.css" rel="stylesheet">
</head>
<body data-spy="scroll" data-target=".bs-docs-sidebar">
<div class="container">
    <div class="row">
        <div class="span12 accordion" id="output">
            {% for cmd in grouped_command.keys() %}
                <div class="accordion-group">
                    <div class="accordion-heading">
                        <a class="accordion-toggle" data-toggle="collapse" data-parent="#accordion2" href="#{{ cmd }}">{%- for line in grouped_command[cmd] %}{{ line }}</br>{% endfor -%}</a>
                    </div>
                    <div id="{{ cmd }}" class="accordion-body collapse {%- if loop.index == 1 %} in {% endif -%}">
                        <div class="accordion-inner">
                            <pre>{%- for line in grouped_output[cmd] %}{{ line }}{% endfor -%}</pre>
                        </div>
                    </div>
                </div>
            {% endfor %}
        </div>
    </div>
</div>
<style>
    .accordion-toggle:hover {
        text-decoration:none;
    }
</style>
<script src="http://twitter.github.com/bootstrap/assets/js/jquery.js"></script>
<script type="text/javascript" src="http://platform.twitter.com/widgets.js"></script>
<script src="http://twitter.github.com/bootstrap/assets/js/bootstrap-collapse.js"></script>
</body>
</html>
"""

def main():
    log_file = sys.argv[1]
    commands_output = OrderedDefaultdict(list)
    CMD_FIRST_CHAR = '+'

    with open(log_file, 'r') as logfile:
        cmd_out = commands_output['']
        for line in logfile:
            if line.startswith(CMD_FIRST_CHAR):
                cmd_out = commands_output[line.replace(CMD_FIRST_CHAR, '$ ').lstrip('\n').strip()]
            else:
                cmd_out.append(line)

    grouped_output = OrderedDict()
    grouped_command = OrderedDict()

    group_cmd = []
    group_output = []

    for cmd, output in commands_output.iteritems():
        group_cmd.append(cmd)
        group_output += output

        if output:
            index = md5.md5(repr(group_output)).hexdigest()
            grouped_output[index] = group_output
            grouped_command[index] = group_cmd
            group_cmd = []
            group_output = []

    template = Template(command_template_table)
    print template.render(grouped_output=grouped_output, grouped_command=grouped_command)


if __name__ == '__main__':
    main()