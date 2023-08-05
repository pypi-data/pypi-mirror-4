from cython_gsl cimport *

ctypedef double * double_ptr
ctypedef void * void_ptr

cdef class FunctionWrapper:
    cdef object function
    cdef object args

def integrate(func, *args):
    cdef double result, error
    cdef gsl_integration_workspace * W
    W = gsl_integration_workspace_alloc(1000)
    cdef gsl_function F
    cdef size_t n_args = len(args)

    cdef double params[n_args]

    for i, arg in enumerate(args):
        params[i] = arg

    F.function = &func_wrapper
    F.params = params

    gsl_integration_qag(&F, lower, upper, 1e-4, 1e-4, 5000, GSL_INTEG_GAUSS41, W, &result, &error)
    gsl_integration_workspace_free(W)

    return result

cdef double eval_cexgauss(double x, void * params) nogil:
    cdef double imu_go, isigma_go, itau_go, imu_stop, isigma_stop, itau_stop, issd
    cdef double p
    imu_go = (<double_ptr> params)[0]
    isigma_go = (<double_ptr> params)[1]
    itau_go = (<double_ptr> params)[2]
    imu_stop = (<double_ptr> params)[3]
    isigma_stop = (<double_ptr> params)[4]
    itau_stop = (<double_ptr> params)[5]
    issd = (<double_ptr> params)[6]

    p = exp(ExGauss_cdf(x, imu_go, isigma_go, itau_go)) * exp(ExGauss_pdf(x, imu_stop+issd, isigma_stop, itau_stop))

    return p


    params[0] = imu_go
    params[1] = isigma_go
    params[2] = itau_go
    params[3] = imu_stop
    params[4] = isigma_stop
    params[5] = itau_stop
    params[6] = issd

    F.function = &eval_cexgauss
    F.params = params

    gsl_integration_qag(&F, lower, upper, 1e-4, 1e-4, 5000, GSL_INTEG_GAUSS41, W, &result, &error)
    gsl_integration_workspace_free(W)
