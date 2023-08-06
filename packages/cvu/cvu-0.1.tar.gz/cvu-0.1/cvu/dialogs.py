# (C) Roan LaPlante 2013 rlaplant@nmr.mgh.harvard.edu


from traits.api import HasTraits,Bool,Event,File,Int,Str,Directory,Function,Enum
from traits.api import List
from traitsui.api import Handler,View,Item,OKCancelButtons,OKButton,Spring,Group
from traitsui.api import ListStrEditor,CheckListEditor
import os

class SubwindowHandler(Handler):
	def closed(self,info,is_ok):
		info.object.finished=is_ok
		info.object.notify=True

class InteractiveSubwindow(HasTraits):
	finished=Bool(False)
	notify=Event
	
class AdjmatChooserWindow(InteractiveSubwindow):
	Please_note=Str("All but first field are optional.  Specify adjmat order "
		"if the desired display order differs from the existing matrix order."
		"  Specify unwanted channels as 'delete' in the label order.  Data "
		"field name applies to the data field for .mat matrices only.")
	adjmat=File
	#adjmat_order=Trait(None,None,File)
	adjmat_order=File
	max_edges=Int
	field_name=Str('adj_matrices')
	ignore_deletes=Bool
	traits_view=View(
		Item(name='Please_note',style='readonly',height=140,width=250),
		Item(name='adjmat'),
		Item(name='adjmat_order',label='Label Order'),
		Item(name='max_edges',label='Max Edges'),
		Item(name='field_name',label='Data Field Name'),
		Item(name='ignore_deletes',label='Ignore deletes'),
		kind='live',buttons=OKCancelButtons,handler=SubwindowHandler(),
		title='Report all man-eating vultures to security',)

class ParcellationChooserWindow(InteractiveSubwindow):
	Please_note=Str('Unless you are specifically interested in the'
		' morphology of an individual subject, it is recommended to use'
		' fsaverage5 and leave the first two fields alone.')
	SUBJECTS_DIR=Directory('./')
	SUBJECT=Str('fsavg5')
	labelnames_f=File
	parcellation_name=Str
	traits_view=View(
		Group(
			Item(name='Please_note',style='readonly',height=85,width=250),
			Item(name='SUBJECT'),
			Item(name='SUBJECTS_DIR'),
			Item(name='parcellation_name',label='Parcellation'),
			Item(name='labelnames_f',label='Label Display Order'),
		), kind='live',buttons=OKCancelButtons,handler=SubwindowHandler(),
			title="This should not be particularly convenient",)

class LoadGeneralMatrixWindow(InteractiveSubwindow):
	Please_note=Str('Same rules for adjmat ordering files apply')
	mat=File
	mat_order=File
	field_name=Str
	ignore_deletes=Bool
	whichkind=Enum('modules','scalars')
	traits_view=View(
		Item(name='Please_note',style='readonly',height=50,width=250),
		Item(name='mat',label='Filename'),
		Item(name='mat_order',label='Ordering file'),
		Item(name='field_name',label='Data field name'),
		Item(name='ignore_deletes',label='Ignore deletes'),
		kind='live',buttons=OKCancelButtons,handler=SubwindowHandler(),
		title='Behold the awesome power of zombies')
	
class NodeChooserWindow(InteractiveSubwindow):
	node_list=List(Str)
	cur_node=Int(-1)
	traits_view=View(
		Item(name='node_list',editor=
			ListStrEditor(selected_index='cur_node'),show_label=False),
		kind='live',height=350,width=350,buttons=OKCancelButtons,
		handler=SubwindowHandler(),
		resizable=True,title='Do you know the muffin man?')

class ModuleChooserWindow(InteractiveSubwindow):
	module_list=List(Str)
	cur_mod=Int(-1)
	traits_view=View(
		Item(name='module_list',editor=
			ListStrEditor(editable=True,selected_index='cur_mod'),show_label=False),
		kind='live',height=350,width=350,buttons=OKCancelButtons,
		handler=SubwindowHandler(),
		resizable=True,title='Roll d12 for dexterity check')

class ModuleCustomizerWindow(InteractiveSubwindow):
	initial_node_list=List(Str)
	intermediate_node_list=List(Str)
	return_module=List(Int)
	traits_view=View(
		Item(name='intermediate_node_list',editor=CheckListEditor(
			name='initial_node_list',cols=2),show_label=False,style='custom'),
		kind='live',height=400,width=500,buttons=OKCancelButtons,
		handler=SubwindowHandler(),
		resizable=True,scrollable=True,title='Mustard/Revolver/Conservatory')

	#index_convert may return a ValueError if the code is buggy, it should be
	#contained in try/except from higher up.
	def index_convert(self):
		self.return_module=[self.initial_node_list.index(i) \
			for i in self.intermediate_node_list]

class SaveSnapshotWindow(InteractiveSubwindow):
	savefile=Str(os.environ['HOME']+'/')
	dpi=Int(300)
	whichplot=Enum('mayavi','chaco','circ')
	traits_view=View(Group(
		Item(name='savefile'),
		Item(name='dpi'),
	), kind='live',buttons=OKCancelButtons,handler=SubwindowHandler(),
		title="Help I'm a bug",height=250,width=250)

class ReallyOverwriteFileWindow(InteractiveSubwindow):
	Please_note=Str('That file exists.  Really overwrite?')
	save_continuation=Function # Continuation passing style
	traits_view=View(Spring(),
		Item(name='Please_note',style='readonly',height=25,width=250,
			show_label=False),
		Spring(),
		kind='live',buttons=OKCancelButtons,handler=SubwindowHandler(),
		title='Your doom awaits you')

class ErrorDialogWindow(HasTraits):
	message=Str
	traits_view=View(Item(name='error',style='readonly'),
		buttons=[OKButton],kind='nonmodal',height=150,width=300,
		title='Evil mutant zebras did this',)
