from cython_gsl cimport *

def main():
    print gsl_sf_gegenpoly_1(0.5, 0.3)
