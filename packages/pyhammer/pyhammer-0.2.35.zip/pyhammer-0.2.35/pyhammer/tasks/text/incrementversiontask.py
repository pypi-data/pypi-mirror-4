import re
from pyhammer.tasks.taskbase import TaskBase

class IncrementVersionTask(TaskBase):

    def __init__( self, assemblyPath, type, blockCount = 4 ):
        super().__init__()
        self.__assemblyPath = assemblyPath
        self.__type = type
        self.__blockCount = blockCount

    def do( self ):
        items = []
        if type(self.__assemblyPath) is str:
            items.append(self.__assemblyPath)
        else:
            items = self.__assemblyPath

        for i, item in enumerate( items ):
            if not self.process(item):
                return False
        return True

    def process( self, item ):
        f = open(item, 'r')
        content = f.read()
        f.close()

        new = ""
        old = ""

        if self.__blockCount == 4:
            version = re.search( '(\d+)\.(\d+)\.(\d+)\.(\d+)', content )

            if not version:
                self.reporter.failure("Can not found version in file: %s" % self.__assemblyPath)

            major = int(version.group(1))
            minor = int(version.group(2))
            revis = int(version.group(3))
            build = int(version.group(4))
            old = version.group(0)

            if self.__type == "minor":
                minor += 1
                revis = 0
            elif self.__type == "revision":
                revis += 1
            elif self.__type == "build":
                build += 1
            else:
                self.reporter.failure("Version block not found: %s" % self.__type)
                return False

            new = str(major) + "." + str(minor) + "." + str(revis) + "." + str(build)

        elif self.__blockCount == 3:
            version = re.search( '(\d+)\.(\d+)\.(\d+)', content )

            if not version:
                self.reporter.failure( "Can not found version in file: %s" % self.__assemblyPath )

            major = int(version.group(1))
            minor = int(version.group(2))
            revis = int(version.group(3))
            old = version.group(0)

            if self.__type == "minor":
                minor += 1
                revis = 0
            elif self.__type == "revision":
                revis += 1
            else:
                self.reporter.failure("Version block not found: %s" % self.__type)
                return False

            new = str(major) + "." + str(minor) + "." + str(revis)
        
        content = content.replace(old,new)

        self.reporter.message( "Changing from version %s to %s" % ( old, new ) )
        
        f = open(item, 'w')
        f.write(content)
        f.close()
        
        return True