import warnings
from .collection import TaxonSet
from .base import Taxon

def add_info_nested(taxon, info, ds_name):
    """Passed to combine_datasets as the add_info parameter, to nest information
    by source dataset.
    """
    taxon.info[ds_name] = info

def add_info_flat(taxon, info, ds_name):
    """Passed to combine_datasets as the add_info parameter, to combine
    information into a flat dictionary.
    """
    for k, v in info.items():
        if k in taxon.info:
            k = str(k) + ' ['+ds_name+']'
        taxon.info[k] = v

def combine_datasets(target_ds, background_ds, distrib_ds_name,
                                                    add_info=add_info_nested):
    """Combine several taxa datasets into one.
    
    Parameters:
        target_ds, background_ds :
          Each should be a sequence of 2-tuples, (name, taxonset). The name will be
          used as the key in the taxa's info. All taxa from any target dataset are
          included in the output, whereas information from background datasets is
          only copied to taxa in target datasets. There must be at least one target
          dataset, and at least one other (either target or background).
          
          Target datasets may be any iterable collection of taxa. Background datasets
          should be TaxonSets or similar.
        
        distrib_ds_name : str
          The name of the dataset from which distribution information should be
          taken, or 'all' to combine distribution info from all datasets.
        
        add_info : func
          A function to combine the information dicts for a taxon. It takes 
          three parameters: the taxon object, the information dict to be added,
          and the name of a dataset.
          
          The default will nest information under the names of the datasets. The
          :func:`add_info_flat` function will make a flat dictionary.
    
    Returns: A :class:`TaxonSet`.
    """
    def _check_distrib_ds(dsname):
        return (dsname == distrib_ds_name) or (distrib_ds_name == 'all')

    output = TaxonSet()

    for dsname, ds in target_ds:
        is_distrib_ds = _check_distrib_ds(dsname)
        for tax in ds:
            if tax.name in output:
                t2 = output[tax.name]
                add_info(t2, tax.info, dsname)
                if is_distrib_ds:
                    t2.distribution.update(tax.distribution)
            else:
                newtax = Taxon(tax.name)
                add_info(newtax, tax.info, dsname)
                if is_distrib_ds:
                    newtax.distribution.update(tax.distribution)
                output.add(newtax)

    for dsname, ds in background_ds:
        is_distrib_ds = _check_distrib_ds(dsname)
        for tax in output:
            try:
                t2 = ds.get_by_accepted_name(tax.name)
            except KeyError:
                warnings.warn("Some taxon could not be found in a background "
                              "dataset - you may need to match the taxa first.")
                continue
            
            add_info(tax, t2.info, dsname)
            if is_distrib_ds:
                tax.distribution.update(t2.distribution)
    
    return output
