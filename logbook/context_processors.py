from .forms import SearchBarForm

"""
Context processor which renders the search bar form.
"""
def search_bar(request):
    search_form = SearchBarForm()
    return {'search_bar':search_form}

def creators(request):
    return {'creators':'Created by Coders for Causes Members: Samuel J S Heath, Lachlan Walking and Zen Ly'}
