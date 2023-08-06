import shelve, os, errno
import atexit
import warnings

import taxonome
from taxonome.config import config
from taxonome.tracker import noop_tracker

user_choice_file = os.path.expanduser(config['cache']['user-choices'])
try:
    os.makedirs(os.path.dirname(user_choice_file), exist_ok=True)
except OSError as e:
    if e.errno != errno.EEXIST:
        raise

user_choices = shelve.open(user_choice_file)
atexit.register(user_choices.close)

def no_op(*args): pass

class TryAnotherName(Exception):
    """This is raised if the user, when prompted, opts to try another name."""
    def __init__(self, newname):
        self.newname = newname
    def __str__(self):
        return "User asked to try another name, but code can't handle that here."

class AmbiguousMatchesError(KeyError):
    pass

class NameSelector:
    """Choose one from a list of possible matching names. If necessary, this
    will ask the user for interactive input. See the __call__ docstring for
    more details.
    
    This is used by the .select() and .optimistic_select() methods
    of TaxonSet objects."""
    def __init__(self, previous_choices=user_choices):
        """Set up the object for picking between alternative matching names.
        
        Parameters
        ----------
        previous_choices : mapping or None
          A mapping which can be used to record and repeat previous selections
          made by the user. By default, this uses a shelf, a persistent
          key-value store on disk. If None, this will be disabled.
        """
        super().__init__()
        self.previous_choices = previous_choices
    
    def __call__(self, name_options, name, allow_retype=True, tracker=noop_tracker):
        """Master function to select one name from a number of possibilities.
        
        Parameters
        ----------
        name_options : list
          A list of 2-tuples, (synonym, accepted_name), as returned by
          :meth:`TaxonSet.resolve_name`.
        name : Name or str
          The name we're trying to match.
        allow_retype : bool
          If True, offers the user the option to manually enter a new name. A
          TryAnotherName exception is raised; its 'newname' parameter contains
          the new name entered.
        tracker :
          A tracker object (see :mod:`taxonome.tracker`) to record the name
          selection process.
        
        Returns
        -------
        A 2-tuple, (synonym, accepted_name). Raises KeyError if name_options is
        empty or the user rejects all options. Raises TryAnotherName if the
        user chooses to enter a new name to search for.
        """
        rawname = name.plain if isinstance(name, taxonome.Name) else name
        
        def track_steps(selname, acc_name, main_method):
            """Calls tracker.name_transform for:
            - Fuzzy name matching (if applicable)
            - The selected name match, with main_method as the method
            - Syonymy (if matched name is not the accepted name)
            """
            if rawname != selname.plain:
                tracker.name_transform(rawname, selname.plain, "name variation")
            tracker.name_transform(name, selname, main_method)
            if selname != acc_name:
                tracker.name_transform(selname, acc_name, "synonymy")
        
        if not(name_options):                   # No options
            raise KeyError("No matching names", name)
            
        if len(name_options) == 1:              # One option (in list)
            n, an = name_options[0]
            track_steps(n, an, "one match")
            return name_options[0]
        
        an1 = name_options[0][1]                # All options are equivalent
        if all(an == an1 for n, an in name_options[1:]):
            n = name_options[0][0]
            track_steps(n, an1, "matches point to same taxon")
            return name_options[0]
        
        if self.previous_choices is not None and name is not None:
            choice = self.get_previous_choice(name_options, name, tracker)
            if choice is not None:
                track_steps(choice[0], choice[1], "recalled user selection")
                return choice
        
        try:
            choice = self.user_select(name_options, name, allow_retype=allow_retype,
                                    tracker=tracker)
        except NotImplementedError:
            warnings.warn("Ambiguous names, user selection not enabled.")
            raise AmbiguousMatchesError(name)
        
        track_steps(choice[0], choice[1], "user selection")
        return choice
        
    def get_previous_choice(self, name_options, name, tracker):
        try:
            prevoptions, prevchoice = self.previous_choices[repr(name)]
        except KeyError:
            return
        
        if prevoptions == set(name_options):
            if isinstance(prevchoice, Exception):
                # User selected one of the 'special' options.
                if isinstance(prevchoice, TryAnotherName):
                    tracker.name_transform(name, prevchoice.newname, "recalled user input")
                raise prevchoice
            # User selected one of the regular options:
            return prevchoice
    
    def store_user_choice(self, name_options, name, choice):
        if self.previous_choices is not None:
            self.previous_choices[repr(name)] = (set(name_options), choice)
        if hasattr(self.previous_choices, 'sync'):
            self.previous_choices.sync()
    
    def user_select(self, name_options, name, allow_retype, tracker):
        """This should be overridden by subclasses to let the user pick names
        interactively.
        
        Parameters:
          name_options: list
            Pairs of (matching_name, accepted_name).
          name: str
            The name that we're trying to match.
          allow_retype: bool
            If True, offer the user the option to type another name to search for.
          tracker:
            A tracker object - see details in :mod:`taxonome.tracker`.
        
        Returns:
          The pair of (matching_name, accepted_name) the user selected. Raises
          KeyError if the user rejected all choices.
        """
        raise NotImplementedError

class TerminalNameSelector(NameSelector):
    """Subclass of NameSelector presenting a terminal interface to let the
    user pick between alternative names."""
    def user_select(self, name_options, name, allow_retype, tracker):
        """Allow the user to choose between the options interactively."""
        def cache_choice(choice):
            self.store_user_choice(name_options, name, choice)
        
        if name:                            # Choose from multiple options
            print("== Select a match for {0}: ==".format(name))
        else:
            print("==Select a match: ==")
        print("N", "(Reject all)")
        if allow_retype:
            print(0, "(Specify new name to search for)")
        
        for i, (pname, pname_acc) in enumerate(name_options, start=1):
            if pname_acc and pname != pname_acc:
                print (i, pname, "\t  ->", pname_acc)
            else:
                print(i, pname)
                
        def _isvalid(inp):
            return (inp.isnumeric() and int(inp) >= 0 \
                        and int(inp) <= len(name_options)) \
                    or inp.upper() == "N"
        
        inp = input("Enter a number: ")
        while not _isvalid(inp):
            inp = input("Try again! Number: ")
        
        if inp.upper() == "N":
            ke = KeyError("User rejected all options", name)
            cache_choice(ke)
            raise ke
        if int(inp) == 0:
            newname = input("New name? ")
            tracker.name_transform(name, newname, "user input")
            retry = TryAnotherName(newname)
            cache_choice(retry)
            raise retry
        
        n, accname = name_options[int(inp)-1]
        cache_choice((n, accname))
        return n, accname
