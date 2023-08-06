try:
    import despotic

    def despotic_model(xarr, cloud, cloudpars, species, frequency, bandwidth):

        line = cloud.lineLum(species)

