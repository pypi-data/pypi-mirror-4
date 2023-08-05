# -*- coding: utf-8 -*-
import mock

import argh


# just unit/mock tests
def test_mock_checkout():
    p = argh.ArghParser()
    p.add_argument = mock.MagicMock()

    @argh.arg('foo', default=1, nargs='+')
    def cmd(args):
        pass

    argh.set_default_command(p, cmd)
    p.add_argument.assert_called_with('foo', default=1, nargs='+', type=int)
