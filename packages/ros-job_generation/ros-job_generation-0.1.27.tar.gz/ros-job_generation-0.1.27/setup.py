from setuptools import setup

setup(name='ros-job_generation',
      version= '0.1.27',
      install_requires=['python-jenkins', 'rospkg', 'rosdep'],
      packages=['job_generation'],
      package_dir = {'':'src'},
      scripts = ['scripts/generate_devel.py',
                 'scripts/generate_postrelease.py',
                 'scripts/generate_prerelease.py',
                 'scripts/generate_rosinstall.py',
                 'scripts/generate_unreleased.py',
                 'scripts/run_auto_stack_devel.py',
                 'scripts/run_auto_stack_prerelease.py',
                 'scripts/run_auto_stack_postrelease.py',
                 'scripts/run_auto_stack_unreleased.py',
                 ],
      author = "Wim Meeussen",
      author_email = "wim@willowgarage.com",
      url = "http://www.ros.org/wiki/job_generation",
      download_url = "http://pr.willowgarage.com/downloads/",
      keywords = ["ROS"],
      classifiers = [
        "Programming Language :: Python",
        "License :: OSI Approved :: BSD License" ],
      description = "build farm job generation for dry jobs",
      long_description = """\
build farm job generation for dry jobs
""",
      license = "BSD"
      )
