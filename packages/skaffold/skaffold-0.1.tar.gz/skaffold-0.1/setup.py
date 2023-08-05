from distutils.core import setup

setup(name="skaffold", 
      version="0.1", 
      description="Flask/SQLAlchemy Admin Scaffold",
      author="Christian Fernandez",
      author_email="chriszf@gmail.com",
      url="http://chriszf.github.com/skaffold",
      packages=["skaffold"],
      platforms="any",
      install_requires=[
        "Flask>=0.9",
        "Flask-WTF>=0.8",
        "Jinja2>=2.6",
        "SQLAlchemy>=0.7.9"],
      package_data={"skaffold": ["templates/*.html"]},
      )
