def backup_file(pth, storedat=None):
    '''Store a copy of the original and return that location'''
    if storedat is None:
        # get an unused file name to store the original
        storedat = backup_path(pth)
    logging.debug('copying original to %s', storedat)
    ignore_file(storedat)
    pth.copy(storedat)
    # check if the copy was successful
    if not same_file(pth, storedat):
        raise ValueError('copy seems to differ from original')
    return storedat

def store_original_location(pth, storedat):
    '''store the original path so we can revert it later'''
    store.originals[pth] = storedat
    store.storedat[storedat] = None

def backup_path(pth):
    '''Take the original path and create a backup path for it'''
    return make_path(pth).abspath()

