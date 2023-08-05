#!/usr/bin/python

# test Alfresco

import sys
from alfREST import RESTHelper, ROLES

if len(sys.argv) != 6:
    print "Usage:\n"
    print "test.py username password host port path\n"
    print "es.\n"
    print "test.py admin alfresco 127.0.0.1 8080 /Sites/mysite/documentLibrary/test\n"
    exit(1)
    
_, login, password, host, port, path = sys.argv

# login
rh = RESTHelper()
rh.login(login, password, host, port)

# createFolder
folderOid = rh.createFolder(path, "testfolder")
path = path + "/testfolder"

# createDocument (sio could be a file object...)
from StringIO import StringIO
sio = StringIO()
sio.write("Well, that's all folks.")
sio.seek(0)
sio.name = "test.txt"
tkns = path.split("/")
siteId = tkns[2]
containerId = tkns[3]
uploadDirectory = "/".join(tkns[4:])
idObject = rh.fileUpload(sio, siteId, containerId, "/%s" % uploadDirectory)
sio.close()

# get properties
props = rh.getProperties("%s/test.txt" % path)
assert props["cmis:createdBy"] == login

# get content
content = rh.getContent("%s/test.txt" % path)
assert content == "Well, that's all folks."

# get content by id
content = rh.getContent(idObject)
assert content == "Well, that's all folks."


# add a tag to the document
rh.addTag("workspace", "SpacesStore", idObject, "tag_test")
tags = rh.getNodeTags("workspace", "SpacesStore", idObject)
assert "tag_test" in tags

# list document in folder
children = rh.getChildren(path)
assert children[0]["cmis:name"] == "test.txt"

# list of root groups
groups = rh.listAllRootGroups()
assert groups is not None

# add root group
rh.addRootGroup(u"GROUP_TEST", "Test group")

# set ACL
acl = {}
acl[u'GROUP_TEST'] = [([u"{http://www.alfresco.org/model/content/1.0}cmobject.Consumer",], True),]
rh.applyACL(path, acl)

# get ACL
testACL = rh.getACL(path)
assert u'GROUP_TEST' in testACL.keys()

# add person
rh.addPerson("supermario", "mario", "super", "supermario@nintendo.com", "imsuper")

# add user to group
rh.addGroupOrUserToGroup(u"supermario", u"GROUP_TEST")

# list users in group
users = rh.listChildAuthorities(u"GROUP_TEST")
assert len(users) == 1
assert users[0]['fullName'] == "supermario"

# remove user from group
rh.removeAuthorityFromGroup(u"supermario", u"GROUP_TEST")

# list users in group
users = rh.listChildAuthorities(u"GROUP_TEST")
assert len(users) == 0

# delete person
rh.deletePerson("supermario")

# remove ACL
acl = {}
rh.applyACL(path, acl)

# delete root group
rh.deleteRootGroup(u"GROUP_TEST")

# remove tag from the file object
rh.deleteTag("workspace", "SpacesStore", idObject, "tag_test")
assert "tag_test" not in rh.getNodeTags("workspace", "SpacesStore", idObject)

# delete the file object
rh.deleteObject(idObject)

# delete the test folder
rh.deleteObject(folderOid)

# logout
rh.logout()
