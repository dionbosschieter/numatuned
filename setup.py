import os
from setuptools.command.install import install
from setuptools import setup

class CustomerInstaller(install):

  CREATE_DIRS = [
      os.path.join('/lib', 'systemd', 'system'),
  ]

  def run(self):
    """
    Installs and then copies the service file to the systemd directory
    """
    install.run(self)
    print("Creating needed directories")
    for directory in self.CREATE_DIRS:
        if not os.path.exists(directory):
            try:
                os.makedirs(directory)
            except OSError as exc:
                if exc.errno == 13:
                    print("WARNING! Failed to create directory '{}'. This "
                          "might cause problems.".format(directory))
                else:
                    raise

setup(name='numatuned',
      version='0.2',
      description='Numad replacement for qemu/libvirtd virtual machines that uses virsh numatune --nodeset to bind a virtual machine to a numa zone',
      url='http://github.com/dionbosschieter/numatuned',
      author='Dion Bosschieter',
      author_email='dbosschieter@transip.nl',
      license='MIT',
      packages=['numatuned', 'numatuned.provisioning', 'numatuned.provisioning.rules'],
      zip_safe=False,
      scripts=['bin/numatuned'],
      data_files=[('/lib/systemd/system', ['bin/numatuned.service'])],
      cmdclass={'install': CustomerInstaller},
)
