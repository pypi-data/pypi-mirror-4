# -*- coding: utf-8 -*-
import zc.buildout
import zc.recipe.egg


class Recipe:

    def __init__(self, buildout, name, options):
        self.options = options
        self.src_absolute_path = '%s/%s' % (buildout['buildout']['directory'], buildout[name]['src'])
        self.egg = zc.recipe.egg.Scripts(buildout, name, options)

    def install(self):
        requirements, ws = self.egg.working_set()
        external_deps_paths=[f.location for f in ws]
        # src should not be count as an external dependency
        if self.src_absolute_path in external_deps_paths:
            external_deps_paths.remove(self.src_absolute_path)

        with open('.project', 'w') as f:
            f.writelines('''<?xml version="1.0" encoding="UTF-8"?>
<projectDescription>
    <name>%(name)s</name>
    <comment></comment>
    <projects>
    </projects>
    <buildSpec>
    	<buildCommand>
    		<name>org.python.pydev.PyDevBuilder</name>
    		<arguments>
    		</arguments>
    	</buildCommand>
    </buildSpec>
    <natures>
    	<nature>org.python.pydev.pythonNature</nature>
    </natures>
</projectDescription>''' % self.options)

        with open('.pydevproject', 'w') as f:
            f.writelines('''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<?eclipse-pydev version="1.0"?><pydev_project>
<pydev_pathproperty name="org.python.pydev.PROJECT_SOURCE_PATH">
<path>/%(name)s/%(src)s</path>
</pydev_pathproperty>
<pydev_property name="org.python.pydev.PYTHON_PROJECT_VERSION">%(python_version)s</pydev_property>
<pydev_property name="org.python.pydev.PYTHON_PROJECT_INTERPRETER">%(python_interpreter)s</pydev_property>
<pydev_pathproperty name="org.python.pydev.PROJECT_EXTERNAL_SOURCE_PATH">''' % self.options)
            for path in external_deps_paths:
                f.write('''
<path>%s</path>''' % path)
            f.writelines('''
</pydev_pathproperty>
</pydev_project>''')
        return ()

    update = install
