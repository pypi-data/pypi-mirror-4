#!/usr/bin/env python

""" This is a service intended to be run periodically as a CRON job.

    It's purpose is to scan Pivotal Tracker and ReviewBoard and append
    a 'reviewed' label to any story that is finished and all its review requests
    have been approved (there must be at least 1 review request for the story in
    order for the service to notice it).

    The service expects a '${HOME}/.workflow.cfg' file with the following
    structure:

    [auth]
    pt_token = <PT_token>
    rb_user = <reviewboard username>
    rb_pwd = <password for the reviewboard user>

    The users (in PT & RB) should have access to all the projects (otherwise the
    service will not be able to update all the stories).
"""

import os
import gitflow.reviewboard.extensions as rb_ext
import gitflow.busyflow.pivotal as pt
import config
import ConfigParser
import sys, time

from service.daemonize import Daemon

CHECK_INTERVAL = 60 * 5

CFG_FILE = '%s/.workflow.cfg' % os.environ['HOME']


def is_story_approved(story_id, rb_auth):
    return rb_ext.is_story_approved(
        'https://dev.salsitasoft.com/rb', story_id, rb_auth)


def get_unprocessed_stories_from_pt(token, project_id):
    """ Get all finished unreviewed stories in current and backend iterations
        for any project I have access to (...which should be all of them).
    """
    client = pt.PivotalClient(token=pt_token)
    stories = client.stories.all(project_id)['stories']
    finished_unreviewed_stories = []
    for story in stories:
        if 'reviewed' in story['labels']:
            # Skip stories that have already been processed by us.
            continue
        if story['story_type'] == 'chore' and story['current_state'] == 'started':
            # Take care of started chores (they don't have the 'finished'
            # state).
            finished_unreviewed_stories.append(story)
        elif story['current_state'] == 'finished':
            # Handle finished features and bugs.
            finished_unreviewed_stories.append(story)
    return finished_unreviewed_stories


def process_project(pt_token, project_id, rb_auth):
    # We're only interested in stories that are finished and don't have the
    # 'reviewed' label.
    stories = get_unprocessed_stories_from_pt(pt_token, project_id)

    # Filter out stories that have any open review requests.
    approved_stories = [s for s in stories if
        is_story_approved(s.id, rb_auth)]

    # Add a 'reviewed' label to the stories that survived our filtering.
    for s in approved_stories:
        pt.api.append_label_to_a_story(
            project_id, s.id, pt_token, config.pt_reviewed_label)
        if s.story_type == 'chore':
            pt.api.remove_label_from_a_story(
                project_id, s.id, pt_token, config.chore_review_state_label)


def process_stories(pt_token, rb_auth):
    client = pt.PivotalClient(token=pt_token)
    for project in client.projects.all()['projects']:
        process_project(pt_token, project['id'], rb_auth)


class WorkflowDaemon(Daemon):
    def run(self):
        while True:
            # Read the sensitive data from a config file.
            config = ConfigParser.RawConfigParser()
            config.read(CFG_FILE)
            pt_token = config.get('auth', 'pt_token')
            rb_user = config.get('auth', 'rb_user')
            rb_pwd = config.get('auth', 'rb_pwd')
            process_stories(pt_token, {'username': rb_user, 'password': rb_pwd})

            time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    daemon = WorkflowDaemon(
        '/tmp/workflow-service.pid', stdout='/tmp/wf.txt',
        stderr='/tmp/wf_err.txt')
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        else:
            print "Unknown command"
            sys.exit(2)
        sys.exit(0)
    else:
        print "usage: %s start|stop|restart" % sys.argv[0]
        sys.exit(2)
