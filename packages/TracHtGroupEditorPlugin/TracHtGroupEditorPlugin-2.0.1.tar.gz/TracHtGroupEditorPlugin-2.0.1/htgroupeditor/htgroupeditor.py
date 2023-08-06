# -*- coding: utf-8 -*-
""" Trac Groups Editor plugin
  Edit the groups in the group file.
  Select a group
  Display it's contents
  Delete or add listed members
  If the fine grained page permissions plugine is enabled, then
  as an option also update it.
"""


#def print_debug(s):
    #f = open('/srv/trac/project2/log/debug', 'a')
    #f.write(str(s) + '\n')
    #f.close


import os
from configobj import ConfigObj

from acct_mgr.api import AccountManager

from pkg_resources import resource_filename
from trac.core import *
from trac.util import translation
from trac.admin.api import IAdminPanelProvider
from trac.web.chrome import ITemplateProvider, add_stylesheet
from trac.perm import IPermissionGroupProvider

class GroupsEditorPlugin(Component):
    implements(IAdminPanelProvider, ITemplateProvider, IPermissionGroupProvider)

    def __init__(self):
        self.account_manager = AccountManager(self.env)

    # ITemplateProvider methods
    # Used to add the plugin's templates and htdocs 
    def get_templates_dirs(self):
        return [resource_filename(__name__, 'templates')]

    def get_htdocs_dirs(self):
        return []

    # IPermissionGroupProvider methdos
    def get_permission_groups(self, username):
        """Return a list of names of the groups that the user with the specified
        name is a member of."""

        groups_list = []
        groups_dict = self._get_groups_and_members() or {}

        for group,usernames in groups_dict.items():
            if username in usernames:
                groups_list.append(group)
        
        return groups_list

    # IAdminPanelProvider methods
    def get_admin_panels(self, req):
        """Return a list of available admin panels.
            The items returned by this function must be tuples of the form
            `(category, category_label, page, page_label)`.
        """
        if 'TRAC_ADMIN' in req.perm:
            # Simply put, it's what goes in the menu on the left!
            # the page is the name of the page that will be called for the menu entry
            # it will go ...../category/page
            yield ('accounts', translation._('Accounts'), 'groups', translation._('Groups'))


    def _get_filename(self, section, name):
        file_name = self.config.get(section, name)
        if len(file_name):
            if (not file_name.startswith(os.path.sep)) and (not file_name[1] == (':')):
                file_name = os.path.join(self.env.path, file_name)
            return(file_name)
        else:
            return(None)

    def _group_filename(self):
        group_file_name = self._get_filename('account-manager', 'group_file')
        if not group_file_name:
            group_file_name = self._get_filename('htgroups', 'group_file')
        if not group_file_name:
            raise TracError('Group filename not found in the config file. In neither sections\
                                "account-manager" nor "htgroups" under the name "group_file".')
        if not os.path.exists(group_file_name):
            raise TracError('Group filename not found: %s.' % group_file_name)
        return(group_file_name)


    def _get_groups_and_members(self):
        """
        Get the groups and their members as a dictionary of
        lists.
        """
        # could be in one of two places, depending if the 
        # account-manager is installed or not
        group_file_name = self._group_filename()
        groups_dict = dict()
        group_file = file(group_file_name)
        try:
            for group_line in group_file:
                # Ignore blank lines and lines starting with #
                group_line = group_line.strip()
                if group_line and not group_line.startswith('#'):
                    group_name = group_line.split(':', 1)[0]
                    group_members = group_line.split(':', 2)[1].split(' ')
                    groups_dict[group_name] = [ x for x in [member.strip() for member in group_members] if x ]
        finally:
            group_file.close()
        if len(groups_dict):
            return groups_dict
        else:
            return None


    def _write_groups_file(self, entries):
        """
        Write the groups and members to the groups file
        """
        group_file = open(self._group_filename(), 'w')
        for group_name in entries.keys():
            group_file.write(group_name + ': ' + ' '.join(entries[group_name]) + '\n')
        group_file.close()


    def _check_for_finegrained(self):
        """
        Check if the fine grained permission system is installed
        """
        return (self.config.getbool('components', 'authzpolicy.authz_policy.authzpolicy') or
                self.config.getbool('components', 'authz_policy.authzpolicy') )

    def _check_for_svnauthz(self):
        """
        Check if the SVN Authz Plugin is installed
        """
        return self.config.getbool('components','svnauthz.svnauthz.svnauthzplugin')

    def _update_fine_grained(self, group_details):
        #import ConfigObj
        authz_policy_file_name = self._get_filename('authz_policy', 'authz_file')
        authz_policy_dict = ConfigObj(authz_policy_file_name)
        # If there isn't a group file, don't destroy the existing entries
        if (group_details):
            authz_policy_dict['groups'] = group_details
        authz_policy_dict.write()

    def _update_svnauthz(self, group_details):
        svnauthz_policy_file_name = self._get_filename('trac','authz_file')
        svnauthz_policy_dict = ConfigObj(svnauthz_policy_file_name)
        # If there isn't a group file, don't destroy the existing entries
        if (group_details):
            svnauthz_policy_dict['groups'] = group_details
        svnauthz_policy_dict.write()
        

    def render_admin_panel(self, req, cat, page, path_info):
        """
        Render up the panel.
        When applying deletions and additions, additions
        happen post deletions, so additions in effect have
        a higher precedence.  The way it is done, it shouldn't be
        possible to have both 
        """
        req.perm.require('TRAC_ADMIN')
        add_stylesheet(req, 'ge/css/htgroupeditor.css')

        page_args = {}

        group_details = self._get_groups_and_members()
        
        # This option needs to be set if the admin can add and delete groups
        # usage in trac.ini:
        # [htgroupedit]
        # allowgroupedit = enabled
        allowgroupedit = self.config.getbool("htgroupeditor","allowgroupedit")

        # For ease of understanding and future reading
        # being done in the ORDER displayed.
        if not req.method == 'POST':
            groups_list = [''];
            if group_details is not None:
               groups_list = groups_list + group_details.keys()

            page_args['groups_list'] = groups_list
            page_args['allowgroupedit'] = allowgroupedit

            return 'htgroupeditor.html', page_args
        else:
            if req.args.get('new_group') and group_details is None:
                # It can only happen for new_group, that group_details is None
                groups_list = []
                group_details = {}
            else:
                groups_list = group_details.keys()
            
            if req.args.get('new_group') and allowgroupedit:
                # Create new group and select it
                if not req.args.get('new_group_name') or len(str(req.args.get('new_group_name')).strip()) == 0:
                    raise TracError("Group name was empty")
                
                group_name = str(req.args.get('new_group_name')).strip()
                if group_name in group_details.keys():
                    raise TracError("Group already exists")
                
                group_details[group_name] = []
                groups_list.append(group_name)
            elif req.args.get('delete_group') and allowgroupedit:
                # Deleting a group involves removing it from list and details
                delete_group_name = str(req.args.get('group_name')).strip()
                if not delete_group_name in groups_list:
                    raise TracError("Invalid group for deletion")
                
                del group_details[delete_group_name]
                groups_list.remove(delete_group_name)
                
                if len(groups_list) == 0:
                    # In case that was the last group, the subsequent won't work
                    # Thus we have to do the writing of files here and return the empty page
                    self._write_groups_file(group_details)
                    if req.args.get('finegrained_check'):
                        self._update_fine_grained(group_details)
                    if req.args.get('svnauthz_check'):
                        self._update_svnauthz(group_details)
                    
                    # Finally send the empty page
                    page_args['groups_list'] = ['']
                    page_args['allowgroupedit'] = allowgroupedit

                    return 'htgroupeditor.html', page_args
                
                # Select first group in list
                group_name = groups_list[0]
            else:
                # Select group based on the request
                group_name = str(req.args.get('group_name'))
            
            # put the selected entry at the top of the list
            groups_list.remove(group_name)
            groups_list.insert(0, group_name)
            # Get rid of duplicates
            users_list = list()
            for name in group_details[group_name]:
                if name not in users_list:
                    users_list.append(name)
            group_details[group_name] = sorted(users_list)

            if req.args.get('deletions'):
                deletions = req.args.get('deletions')
                # if only on entry it will be a string, so need to make it a list
                if not isinstance(deletions, list):
                    deletions = [deletions]
                for deletion in deletions:
                    # In case there arer multiple entries
                    while deletion in group_details[group_name]:
                        group_details[group_name].remove(deletion)

            if req.args.get('additional_names'):
                additional_names = req.args.get('additional_names')
                if not isinstance(additional_names, list):
                    additional_names = [additional_names]
                #  If a reload is done after an add, a duplicate can be created.
                for name in additional_names:
                    if name not in group_details[group_name]:
                        group_details[group_name].append(name)

            # get the list of users not in the group
            addable_usernames = []
            for username in self.account_manager.get_users():
                username = username.strip()
                if len(username) and not username in group_details[group_name]:
                    addable_usernames.append(username)   

            group_details[group_name].sort()
            addable_usernames.sort()

            page_args['groups_list'] = groups_list
            page_args['users_list'] = group_details[group_name]
            page_args['addable_usernames'] = addable_usernames
            page_args['group_name'] = group_name
            page_args['finegrained'] = self._check_for_finegrained()
            page_args['svnauthz'] = self._check_for_svnauthz()
            page_args['allowgroupedit'] = allowgroupedit

            if req.args.get('apply_changes') or req.args.get('new_group') or req.args.get('delete_group'):
                self._write_groups_file(group_details)
                # update the fine grained permissions, if it is installed    
                if req.args.get('finegrained_check'):
                    self._update_fine_grained(group_details)
                if req.args.get('svnauthz_check'):
                    self._update_svnauthz(group_details)

            return 'htgroupeditor.html', page_args

