#!/usr/bin/env/python2
# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from farnsworth.models import CBTesterJob
from farnsworth.models import ValidPoll

import meister.creators
LOG = meister.creators.LOG.getChild('cb_tester')


class CBTesterCreator(meister.creators.BaseCreator):
    @property
    def jobs(self):
        # Get only polls for which scores have not been computed.
        for poll in ValidPoll.select().where(ValidPoll.has_scores_computed == False):
            target_cs = poll.cs
            # Create job for unpatched binary
            LOG.debug("Yielding CBTesterJob for poll %s (unpatched)", poll.id)
            yield (CBTesterJob(payload={'poll_id': poll.id,
                                        'cs_id': target_cs.id}), 0)

            # For each of patch types create Tester Jobs
            for patch_type in target_cs.cbns_by_patch_type():
                LOG.debug("Yielding CBTesterJob for poll %s (patched %s)", poll.id, patch_type)
                yield (CBTesterJob(payload={'poll_id': poll.id,
                                            'cs_id': target_cs.id,
                                            'patch_type': patch_type}), 0)
            # Set scores computed flag and save
            poll.has_scores_computed = True
            poll.save()
