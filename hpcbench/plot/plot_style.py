import matplotlib.pyplot as plt
from matplotlib import rc


plt.rcParams.update({
    'font.sans-serif': 'Nimbus Sans',
    'font.family': 'sans-serif'
})

class ColourGetter:
    def __init__(self):
        self.colours = ['#377eb8', '#ff7f00', '#4daf4a', '#f781bf', '#a65628',
                        '#984ea3', '#999999', '#e41a1c', '#dede00']
        self.names = {
            'blue':    '#377eb8', 
            'orange':  '#ff7f00',
            'green':   '#4daf4a',
            'pink':    '#f781bf',
            'brown':   '#a65628',
            'purple':  '#984ea3',
            'gray':    '#999999',
            'red':     '#e41a1c',
            'yellow':  '#dede00'
        } 
        
        self.lookup = {
            "amber": "orange",
            "gromacs": "blue",
            "namd": "green",
            "lammps": "purple",
            "openmm": "red",
            "nvidia": "green",
            "amd": "red",
            "archer": "blue",
            "jade": "green",
            "lumi": "red",
            "grace": "green",
            "bede": "green",
            "isambard": "brown"
        }
        
    def get(self, label):
        for key, value in self.lookup.items():
            if key.lower() in label.lower():
                return self.names[value]
            else:
                continue
        colour = self.colours.pop(0)
        self.colours.append(colour)
        return colour

#rc('font',**{'family':'sans-serif','sans-serif':['Nimbus Sans']})

#plt.rcParams['text.usetex'] = True
plt.style.use('bmh')
#plt.rcParams["font.family"] = "sans-serif"
#plt.rcParams["font.sans-serif"] = ["Nimbus Sans"]

#from matplotlib import font_manager
#xticks_font = font_manager.FontProperties(family="sans")



#plt.rcParams['mathtext.rm'] = 'Nimbus Sans'
#rc('mathtext', fontset='custom')
#plt.rcParams['mathtext.fontset'] = 'custom'



#plt.rcParams['mathtext.it'] = 'Nimbus Sans:italic'
#plt.rcParams['mathtext.bf'] = 'Nimbus Sans:bold'

