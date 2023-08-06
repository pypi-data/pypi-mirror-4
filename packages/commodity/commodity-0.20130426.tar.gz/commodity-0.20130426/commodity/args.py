# -*- coding:utf-8; tab-width:4; mode:python -*-
import os
import argparse

import configobj
import validate

from .pattern import Bunch, MetaBunch


class ArgumentConfigParser(argparse.ArgumentParser):
    def __init__(self, *args, **kargs):
        self.specs = None

        if 'specs' in kargs:
            self.specs = kargs.get('specs')
            del kargs['specs']

        super(ArgumentConfigParser, self).__init__(*args, **kargs)
        self.set_specs(self.specs)

    def set_specs(self, specs):
        self.specs = specs
        self.cobj = configobj.ConfigObj(configspec=specs)
        self._validate()

    def load_config_file(self, infile):
#        print 'loading config from %s' % infile
        if not os.path.exists(infile):
            return

        self.load_config(file(infile).read().splitlines())

    def load_config(self, config):
        new = configobj.ConfigObj(config, configspec=self.specs)
#        new.validate(validate.Validator())
#        print "->", new

        self.cobj.merge(new)
        self._validate()

#        print "==>", self.cobj

        for sec in new.sections:
            if sec == 'ui':
                continue

            setattr(args, sec, MetaBunch(new[sec]))

        self.parse_args()

    def _validate(self):
        if self.specs:
            assert self.cobj.validate(validate.Validator())

    def parse_args(self, commandline=None):
        global args

        ns = Bunch()
        if self.cobj is not None:
            try:
                ns = MetaBunch(self.cobj['ui'])
            except KeyError:
                pass

        values = argparse.ArgumentParser.parse_args(self, args=commandline, namespace=ns)
        for key, value in values.items():
            setattr(args, key, value)

        return args

    def add_arguments_from_specs(self):
        assert self.specs, 'specs required'
        specs = configobj.ConfigObj(configspec=self.specs)
        specs.validate(validate.Validator())

        if 'ui' not in specs:
            return

        asdata = configobj.ConfigObj(self.specs)['ui']

        for key, val in specs['ui'].dict().items():
            arg = self.add_argument('--' + key, default=val)

            arg.type = type(val)
            if arg.type is bool:
                arg.action = 'store_true'

            doc = asdata.inline_comments[key]
            if doc:
                arg.help = doc.strip('#')

args = Bunch()
parser = ArgumentConfigParser()
add_argument = parser.add_argument
