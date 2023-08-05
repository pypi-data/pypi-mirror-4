from dexy.dexy_filter import DexyFilter
import json
import shutil
import os
import re

class FilenamesFilter(DexyFilter):
    """
    Creates additional inputs for a list of canonical file names.
    """
    ALIASES = ['filenames']
    INPUT_EXTENSIONS = ['.json']
    OUTPUT_EXTENSIONS = ['.json']

    def process(self):
        prev_file = open(self.artifact.previous_artifact_filepath, "r")
        input_info = json.load(prev_file)
        prev_file.close()

        work_dir = input_info['dir']
        parent_artifact = self.artifact.inputs().values()[0]
        parent_artifact_dir = os.path.dirname(parent_artifact.key)
        for f in input_info['filenames']:
            key_with_ext = os.path.join(parent_artifact_dir, f)
            new_artifact = self.artifact.add_additional_artifact(key_with_ext)
            shutil.copy(os.path.join(work_dir, f), new_artifact.filepath())

        self.artifact.set_data(json.dumps(input_info))

class FilenameFilter(DexyFilter):
    """Generate random filenames to track provenance of data."""
    ALIASES = ['fn']

    def process_text(self, input_text):
        for m in re.finditer("dexy(-{2,})(\S+?)\.([a-z]+)", input_text):
            dashes = m.groups()[0]
            local_key = m.groups()[1]
            ext = m.groups()[2]

            parent_dir = os.path.dirname(self.artifact.name)
            key = os.path.join(parent_dir, local_key)

            key_with_ext = "%s.%s" % (key, ext)

            virtual_files = dict((d.name, d.artifacts[0]) for d in self.artifact.virtual_docs)
            canonical_filenames = dict((a.canonical_filename(), a) for a in self.artifact.inputs().values())
            long_canonical_filenames = dict((a.long_canonical_filename(), a) for a in self.artifact.inputs().values())

            if key_with_ext in self.artifact.inputs().keys():
                artifact = self.artifact.inputs()[key_with_ext]
                self.log.debug("[fn] existing key %s in artifact %s links to file %s" %
                          (key_with_ext, self.artifact.key, artifact.filename()))

            elif key_with_ext in virtual_files.keys():
                artifact = virtual_files[key_with_ext]
                artifact.additional = True
                self.artifact.add_input(key_with_ext, artifact)
                self.log.debug("[fn] using virtual file %s with hash %s" % (artifact.key, artifact.hashstring))

            elif key_with_ext in canonical_filenames.keys():
                artifact = canonical_filenames[key_with_ext]

            elif key_with_ext in long_canonical_filenames.keys():
                artifact = long_canonical_filenames[key_with_ext]

            else:
                self.log.debug("[fn] could not find match for %s" % (key_with_ext))
                artifact = self.artifact.add_additional_artifact(key_with_ext, ext)
                self.log.debug("[fn] created new artifact %s ; links to new file %s" %
                          (key_with_ext, artifact.filename()))

            input_text = input_text.replace(m.group(), artifact.filename())

        # Hack to replace __ with -- in case we want to document how to use this
        # filter, we can't use -- because this will be acted upon.
        for m in re.finditer("dexy__(.+)\.([a-z]+)", input_text):
            key = m.groups()[0]
            ext = m.groups()[1]
            replacement_key = "dexy--%s.%s" % (key, ext)
            input_text = input_text.replace(m.group(), replacement_key)

        return input_text
