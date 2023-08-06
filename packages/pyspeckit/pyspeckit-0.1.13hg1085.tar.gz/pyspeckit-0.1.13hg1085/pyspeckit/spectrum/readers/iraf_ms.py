def open_iraf_ms(pyfits_hdu, wcstype='', specaxis="1",
        errspecnum=None, autofix=True, scale_keyword=None,
        scale_action=operator.div, verbose=False, apnum=0, **kwargs):
    """
    This is open_1d_fits but for a pyfits_hdu so you don't necessarily have to
    open a fits file
    """

    # force things that will be treated as strings to be strings
    # this is primarily to avoid problems with variables being passed as unicode
    wcstype = str(wcstype)
    specaxis = str(specaxis)

    data = pyfits_hdu.data

    if hdr.get('NAXIS') == 3:

    if hdr.get('NAXIS') == 2:
        if isinstance(specnum,list):
            # allow averaging of multiple spectra (this should be modified
            # - each spectrum should be a Spectrum instance)
            spec = ma.array(data[specnum,:]).mean(axis=0)
        elif isinstance(specnum,int):
            spec = ma.array(data[specnum,:]).squeeze()
        else:
            raise TypeError(
                "Specnum is of wrong type (not a list of integers or an integer)." +
                "  Type: %s" %
                str(type(specnum)))
        if errspecnum is not None:
            # SDSS supplies weights, not errors.    
            if hdr.get('TELESCOP') == 'SDSS 2.5-M':
                errspec = 1. / np.sqrt(ma.array(data[errspecnum,:]).squeeze())
            else:       
                errspec = ma.array(data[errspecnum,:]).squeeze()
        else:
            errspec = spec*0 # set error spectrum to zero if it's not in the data

    elif hdr.get('NAXIS') > 2:
        if hdr.get('BANDID2'):
            # this is an IRAF .ms.fits file with a 'background' in the 3rd dimension
            spec = ma.array(data[specnum,apnum,:]).squeeze()
        else:
            for ii in xrange(3,hdr.get('NAXIS')+1):
                # only fail if extra axes have more than one row
                if hdr.get('NAXIS%i' % ii) > 1:
                    raise ValueError("Too many axes for open_1d_fits")
            spec = ma.array(data).squeeze()
        if errspecnum is None: 
            errspec = spec*0 # set error spectrum to zero if it's not in the data
    else:
        spec = ma.array(data).squeeze()
        if errspecnum is None: errspec = spec*0 # set error spectrum to zero if it's not in the data

    if scale_keyword is not None:
        try:
            print "Found SCALE keyword %s.  Using %s to scale it" % (scale_keyword,scale_action)
            scaleval = hdr[scale_keyword]
            spec = scale_action(spec,scaleval)
            errspec = scale_action(errspec,scaleval)
        except (ValueError, KeyError) as e:
            pass

    xarr = None
    if hdr.get('ORIGIN') == 'CLASS-Grenoble':
        # Use the CLASS FITS definition (which is non-standard)
        # http://iram.fr/IRAMFR/GILDAS/doc/html/class-html/node84.html
        # F(n) = RESTFREQ + CRVALi + ( n - CRPIXi ) * CDELTi
        if verbose: print "Loading a CLASS .fits spectrum"
        dv = -1*hdr.get('CDELT1')
        if hdr.get('RESTFREQ'):
            v0 = hdr.get('RESTFREQ') + hdr.get('CRVAL1')
        elif hdr.get('RESTF'):
            v0 = hdr.get('RESTF') + hdr.get('CRVAL1')
        else:
            warn("CLASS file does not have RESTF or RESTFREQ")
        p3 = hdr.get('CRPIX1')
    elif hdr.get(str('CD%s_%s%s' % (specaxis,specaxis,wcstype))):
        dv = hdr['CD%s_%s%s' % (specaxis,specaxis,wcstype)]
        v0 = hdr['CRVAL%s%s' % (specaxis,wcstype)]
        p3 = hdr['CRPIX%s%s' % (specaxis,wcstype)]
        try: # astropy.io.fits is not backwards compatible
            hdr.update('CDELT%s' % specaxis,dv)
        except AttributeError:
            hdr.set('CDELT%s' % specaxis,dv)
        if verbose: print "Using the FITS CD matrix.  PIX=%f VAL=%f DELT=%f" % (p3,v0,dv)
    elif hdr.get(str('CDELT%s%s' % (specaxis,wcstype))):
        dv = hdr['CDELT%s%s' % (specaxis,wcstype)]
        v0 = hdr['CRVAL%s%s' % (specaxis,wcstype)]
        p3 = hdr['CRPIX%s%s' % (specaxis,wcstype)]
        if verbose: print "Using the FITS CDELT value.  PIX=%f VAL=%f DELT=%f" % (p3,v0,dv)
    elif len(data.shape) > 1:
        if verbose: print "No CDELT or CD in header.  Assuming 2D input with 1st line representing the spectral axis."
        # try assuming first axis is X axis
        if hdr.get('CUNIT%s%s' % (specaxis,wcstype)):
            xarr = data[0,:]
            spec = data[1,:]
            if data.shape[0] > 2:
                errspec = data[2,:]
        else:
            raise TypeError("Don't know what type of FITS file you've input; "+
                "its header is not FITS compliant and it doesn't look like it "+
                "was written by pyspeckit.")

    # Deal with logarithmic wavelength binning if necessary
    if xarr is None:
        if hdr.get('WFITTYPE') == 'LOG-LINEAR':
            xconv = lambda v: 10**((v-p3+1)*dv+v0)
            xarr = xconv(np.arange(len(spec)))
        else:
            xconv = lambda v: ((v-p3+1)*dv+v0)
            xarr = xconv(np.arange(len(spec)))
    
    # need to do something with this...
    restfreq = hdr.get('RESTFREQ')
    if restfreq is None: restfreq= hdr.get('RESTFRQ')

    XAxis = make_axis(xarr,hdr,wcstype=wcstype,specaxis=specaxis,**kwargs)

    return spec,errspec,XAxis,hdr

