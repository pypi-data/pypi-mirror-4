import os

from loslassa import __version__, LoslassaProject, EXAMPLE_PROJECT_PATH


def b(projectPath):
    fileList = []
    fileSize = 0
    folderCount = 0
    for root, subFolders, files in os.walk(projectPath):
        folderCount += len(subFolders)
        for file_ in files:
            f = os.path.join(root, file_)
            fileSize = fileSize + os.path.getsize(f)
            print f
            fileList.append(f)

    print "Total Size is {0} bytes".format(fileSize)
    print "Total Files %s " % len(fileList)
    print "Total Folders %s " % (folderCount)


project = LoslassaProject(EXAMPLE_PROJECT_PATH)
projectPath = project.sourcePath._path
a(projectPath)
#b(projectPath)
exit()
