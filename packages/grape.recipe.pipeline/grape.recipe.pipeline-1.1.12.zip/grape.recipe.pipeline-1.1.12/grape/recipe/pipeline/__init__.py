# -*- coding: utf-8 -*-
"""
Buildout recipe grape.recipe.pipeline
"""
import os
from grape.recipe.pipeline import prepare


class Recipe(object):
    """
    Buildout recipe for preparing pipelines.
    """

    def __init__(self, buildout, name, options):
        """
        Store the parameters for the buildout recipe.
        """
        self.buildout = buildout
        self.name = name
        self.options = options
        location = os.path.join(buildout['buildout']['parts-directory'], name)
        options['location'] = location

    def install(self):
        """
        Prepare the pipeline.
        """
        # Create directory
        dest = self.options['location']
        if not os.path.exists(dest):
            os.mkdir(dest)
        prepare.main(self.options, self.buildout)
        return dest

    def update(self):
        """
        Prepare the updated pipeline.
        """
        return self.install()
