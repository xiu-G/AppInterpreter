/*
 * MethodNames.java - part of the GATOR project
 *
 * Copyright (c) 2014, 2015 The Ohio State University
 *
 * This file is distributed under the terms described in LICENSE in the
 * root directory.
 */
package presto.android;

import java.util.Set;

import com.google.common.collect.Sets;

public interface MethodNames {
  public String setContentViewSubSig = "void setContentView(int)";

  public String setContentViewViewSubSig = "void setContentView(android.view.View)";

  public String setContentViewViewParaSubSig = "void setContentView(android.view.View,android.view.ViewGroup$LayoutParams)";

  public String layoutInflaterInflate =
      "<android.view.LayoutInflater: android.view.View inflate(int,android.view.ViewGroup)>";

  public String layoutInflaterInflateBool =
      "<android.view.LayoutInflater: android.view.View inflate(int,android.view.ViewGroup,boolean)>";

  public String viewCtxInflate =
      "<android.view.View: android.view.View inflate(android.content.Context,int,android.view.ViewGroup)>";

  public String viewFindViewById =
      "<android.view.View: android.view.View findViewById(int)>";

  public String actFindViewById =
      "<android.app.Activity: android.view.View findViewById(int)>";

  public String findViewByIdSubSig = "android.view.View findViewById(int)";

  public String setIdSubSig = "void setId(int)";
  
  public String setImageSubSig = "void setImageResource(int)";

  public String addViewName = "addView";

  public String findFocusSubSig = "android.view.View findFocus()";

  //=== post CGO'14

  //--- Menu

  public String onCreateOptionsMenuName = "onCreateOptionsMenu";
  public String onPrepareOptionsMenuName = "onPrepareOptionsMenu";

  public String onOptionsItemSelectedName = "onOptionsItemSelected";
  public String onContextItemSelectedName = "onContextItemSelected";

  public String onCreateOptionsMenuSubsig = "boolean onCreateOptionsMenu(android.view.Menu)";
  public String onPrepareOptionsMenuSubsig = "boolean onPrepareOptionsMenu(android.view.Menu)";
  public String onCloseOptionsMenuSubsig = "void onOptionsMenuClosed(android.view.Menu)";

  public String onOptionsItemSelectedSubSig = "boolean onOptionsItemSelected(android.view.MenuItem)";
  public String onContextItemSelectedSubSig = "boolean onContextItemSelected(android.view.MenuItem)";
  public String onMenuItemSelectedSubSig = "boolean onMenuItemSelected(int,android.view.MenuItem)";

  public String viewOnCreateContextMenuSubSig = "void onCreateContextMenu(android.view.ContextMenu)";
  public String onCloseContextMenuSubsig = "void onContextMenuClosed(android.view.Menu)";

  public String activityOnBackPressedSubSig = "void onBackPressed()";
  public String activityOnSearchRequestedSubSig = "boolean onSearchRequested()";

  public String viewShowContextMenuSubsig = "boolean showContextMenu()";
  public String activityOpenContextMenuSubsig = "void openContextMenu(android.view.View)";
  public String activityOpenOptionsMenuSubsig = "void openOptionsMenu()";
  public String activityCloseOptionsMenuSubsig = "void closeOptionsMenu()";

  public String onActivityResultSubSig = "void onActivityResult(int,int,android.content.Intent)";

  public String onCreateContextMenuName = "onCreateContextMenu";
  public String onCreateContextMenuSubSig = "void onCreateContextMenu(android.view.ContextMenu,android.view.View,android.view.ContextMenu$ContextMenuInfo)";
  public String registerForContextMenuSubSig = "void registerForContextMenu(android.view.View)";
  public String setOnCreateContextMenuListenerName = "setOnCreateContextMenuListener";

  public String menuAddCharSeqSubSig = "android.view.MenuItem add(java.lang.CharSequence)";
  public String menuAddIntSubSig = "android.view.MenuItem add(int)";
  public String menuAdd4IntSubSig = "android.view.MenuItem add(int,int,int,int)";
  public String menuAdd3IntCharSeqSubSig = "android.view.MenuItem add(int,int,int,java.lang.CharSequence)";

  public String menuItemSetTitleCharSeqSubSig = "android.view.MenuItem setTitle(java.lang.CharSequence)";
  public String menuItemSetTitleIntSubSig = "android.view.MenuItem setTitle(int)";
  public String menuItemSetIntentSubSig = "android.view.MenuItem setIntent(android.content.Intent)";

  public String menuFindItemSubSig = "android.view.MenuItem findItem(int)";
  public String menuGetItemSubSig = "android.view.MenuItem getItem(int)";

  public String menuInflaterSig = "<android.view.MenuInflater: void inflate(int,android.view.Menu)>";
  // TODO(tony): add SubMenu stuff.

  //--- TabActivity and so on
  public String getTabHostSubSig = "android.widget.TabHost getTabHost()";

  public String tabHostAddTabSugSig = "void addTab(android.widget.TabHost$TabSpec)";
  public String tabHostNewTabSpecSubSig = "android.widget.TabHost$TabSpec newTabSpec(java.lang.String)";

  public String tabSpecSetIndicatorCharSeqSubSig =
      "android.widget.TabHost$TabSpec setIndicator(java.lang.CharSequence)";
  public String tabSpecSetIndicatorCharSeqDrawableSubSig =
      "android.widget.TabHost$TabSpec setIndicator(java.lang.CharSequence,android.graphics.drawable.Drawable)";
  // API >= 4
  public String tabSpecSetIndicatorViewSubSig =
      "android.widget.TabHost$TabSpec setIndicator(android.view.View)";

  public String tabSpecSetContentIntSubSig = "android.widget.TabHost$TabSpec setContent(int)";
  public String tabSpecSetContentFactorySubSig =
      "android.widget.TabHost$TabSpec setContent(android.widget.TabHost$TabContentFactory)";
  // TODO(tony): it starts a new activity, and gets the root. Worry about this
  //             later.
  public String tabSpecSetContentIntentSubSig = "android.widget.TabHost$TabSpec setContent(android.content.Intent)";

  public String tabContentFactoryCreateSubSig = "android.view.View createTabContent(java.lang.String)";

  //--- ListView and so on
  public String getListViewSubSig = "android.widget.ListView getListView()";

  public String setAdapterSubSig = "void setAdapter(android.widget.ListAdapter)";

  public String getViewSubSig =
      "android.view.View getView(int,android.view.View,android.view.ViewGroup)";

  public String newViewSubSig =
      "android.view.View newView(android.content.Context,android.database.Cursor,android.view.ViewGroup)";

  //--- Some "non-standard" callbacks in the framework
  public String onDrawerOpenedSubsig = "void onDrawerOpened()";

  public String onDrawerClosedSubsig = "void onDrawerClosed()";

  //--- Containers

  public String collectionAddSubSig = "boolean add(java.lang.Object)";
  public String collectionIteratorSubSig = "java.util.Iterator iterator()";
  public String iteratorNextSubSig = "java.lang.Object next()";
  public String mapPutSubSig = "java.lang.Object put(java.lang.Object,java.lang.Object)";
  public String mapGetSubSig = "java.lang.Object get(java.lang.Object)";

  //--- framework handlers
  public String onActivityCreateSubSig = "void onCreate(android.os.Bundle)";
  public String onActivityStartSubSig = "void onStart()";
  public String onActivityRestartSubSig =  "void onRestart()";
  public String onActivityResumeSubSig =  "void onResume()";
  public String onActivityPauseSubSig =  "void onPause()";
  public String onActivityStopSubSig =  "void onStop()";
  public String onActivityDestroySubSig =  "void onDestroy()";
  public String activityOnNewIntentSubSig = "void onNewIntent(android.content.Intent)";

  public String onListItemClickSubSig = "void onListItemClick(android.widget.ListView,android.view.View,int,long)";

  //--- Dialogs
  public String activityShowDialogSubSig = "void showDialog(int)";
  // Added in API level 8
  public String activityShowDialogBundleSubSig = "boolean showDialog(int,android.os.Bundle)";

  public String activityDismissDialogSubSig = "void dismissDialog(int)";
  public String activityRemoveDialogSubSig = "void removeDialog(int)";

  public String activityOnCreateDialogSubSig = "android.app.Dialog onCreateDialog(int)";
  // Added in API level 8
  public String activityOnCreateDialogBundleSubSig = "android.app.Dialog onCreateDialog(int,android.os.Bundle)";

  public String activityOnPrepareDialogSubSig = "void onPrepareDialog(int,android.app.Dialog)";
  // Added in API level 8
  public String activityOnPrepareDialogBundleSubSig = "void onPrepareDialog(int,android.app.Dialog,android.os.Bundle)";


  public String dialogOnCancelSubSig = "void onCancel(android.content.DialogInterface)";
  public String dialogOnDismissSubSig = "void onDismiss(android.content.DialogInterface)";
  public String dialogOnKeySubSig = "boolean onKey(android.content.DialogInterface,int,android.view.KeyEvent)";
  public String dialogOnShowSubSig = "void onShow(android.content.DialogInterface)";

  public Set<String> dialogNonLifecycleMethodSubSigs = Sets.newHashSet(
      dialogOnCancelSubSig, dialogOnDismissSubSig,
      dialogOnKeySubSig, dialogOnShowSubSig);

  // This is called by onClick of a button in the dialog
  public String dialogOnClickSubSig = "void onClick(android.content.DialogInterface,int)";

  public String onDialogCreateSubSig = onActivityCreateSubSig;
  public String onDialogStartSubSig = onActivityStartSubSig;
  public String onDialogStopSubSig = onActivityStopSubSig;

  public Set<String> dialogLifecycleMethodSubSigs = Sets.newHashSet(
      onDialogCreateSubSig, onDialogStartSubSig, onDialogStopSubSig);

  public String alertDialogSetButtonCharSeqMsgSubSig =
      "void setButton(java.lang.CharSequence,android.os.Message)";
  public String alertDialogSetButtonIntCharSeqListenerSubSig =
      "void setButton(int,java.lang.CharSequence,android.content.DialogInterface$OnClickListener)";
  public String alertDialogSetButtonCharSeqListenerSubSig =
      "void setButton(java.lang.CharSequence,android.content.DialogInterface$OnClickListener)";
  public String alertDialogSetButtonIntCharSeqMsgSubSig =
      "void setButton(int,java.lang.CharSequence,android.os.Message)";
  public String alertDialogSetButton2ListenerSubSig =
      "void setButton2(java.lang.CharSequence,android.content.DialogInterface$OnClickListener)";
  public String alertDialogSetButton2MessageSubSig =
      "void setButton2(java.lang.CharSequence,android.os.Message)";
  public String alertDialogSetButton3ListenerSubSig =
      "void setButton3(java.lang.CharSequence,android.content.DialogInterface$OnClickListener)";
  public String alertDialogSetButton3MessageSubSig =
      "void setButton3(java.lang.CharSequence,android.os.Message)";

  // Intents
  public String intentAddFlagsSubSig = "android.content.Intent addFlags(int)";
  public String intentSetFlagsSubSig = "android.content.Intent setFlags(int)";
  public String intentGetFlagsSubsig = "int getFlags()";

  // start activity
  public String activityStartActivityForResultSubSig = "void startActivityForResult(android.content.Intent,int)";

  // Sensor
  public String getDefaultSensorSig =
          "<android.hardware.SensorManager: android.hardware.Sensor getDefaultSensor(int)>";

  public String getDefaultSensor2Sig =
          "<android.hardware.SensorManager: android.hardware.Sensor getDefaultSensor(int,boolean)>";

    //add by me
  // TextView.setText
  String textViewSetTextSubSig1 = "void setText(java.lang.CharSequence)";
  String textViewSetTextSubSig2 = "void setText(java.lang.CharSequence,android.widget.TextView$BufferType)";
  String textViewSetTextSubSig3 = "void setText(int)";
  String textViewSetTextSubSig4 = "void setText(int,android.widget.TextView$BufferType)";
  String textViewSetTextSubSig5 = "void setText(char[],int,int)";

  // TextView.setHint
  String textViewSetHintSubSig1 = "void setHint(java.lang.CharSequence)";
  String textViewSetHintSubSig2 = "void setHint(int)";

  // StringBuilder.append()
  // TODO: more varieties of append op
  String stringBuilderAppendSig1 = "<java.lang.StringBuilder: java.lang.StringBuilder append(java.lang.String)>";
  String stringBuilderAppendSig2 = "<java.lang.StringBuilder: java.lang.StringBuilder append(java.lang.Object)>";

  // Fragment transaction
  public String add01AppSupportFragmentTransactionSubSig = "android.support.v4.app.FragmentTransaction add(android.support.v4.app.Fragment,java.lang.String)";
  public String add01FragmentTransactionSubSig = "android.app.FragmentTransaction add(android.app.Fragment,java.lang.String)";

  public String add02AppSupportFragmentTransactionSubSig = "android.support.v4.app.FragmentTransaction add(int,android.support.v4.app.Fragment,java.lang.String)";
  public String add02FragmentTransactionSubSig = "android.app.FragmentTransaction add(int,android.app.Fragment,java.lang.String)";

  public String add03AppSupportFragmentTransactionSubSig = "android.support.v4.app.FragmentTransaction add(int,android.support.v4.app.Fragment)";
  public String add03FragmentTransactionSubSig = "android.app.FragmentTransaction add(int,android.app.Fragment)";

  public String attachAppSupportFragmentTransactionSubSig = "android.support.v4.app.FragmentTransaction attach(android.support.v4.app.Fragment)";
  public String attachFragmentTransactionSubSig = "android.app.FragmentTransaction attach(android.app.Fragment)";

  public String replace01AppSupportFragmentTransactionSubSig = "android.support.v4.app.FragmentTransaction replace(int,android.support.v4.app.Fragment,java.lang.String)";
  public String replace01FragmentTransactionSubSig = "android.app.FragmentTransaction replace(int,android.app.Fragment,java.lang.String)";

  public String replace02AppSupportFragmentTransactionSubSig = "android.support.v4.app.FragmentTransaction replace(int,android.support.v4.app.Fragment)";
  public String replace02FragmentTransactionSubSig = "android.app.FragmentTransaction replace(int,android.app.Fragment)";

  //--- Preference
  public String addPreferencesFromResourceSubSig = "void addPreferencesFromResource(int)";
  public String setPreferencesFromResourceSubSig = "void setPreferencesFromResource(int,java.lang.String)";
  public String onBuildHeadersSubSig = "void onBuildHeaders(java.util.List)";
  public String loadHeadersFromResourceSubSig = "void loadHeadersFromResource(int,java.util.List)";
  public String onCreatePreferencesSubSig = "void onCreatePreferences(android.os.Bundle,java.lang.String)";
  public String findPreferenceSubSig = "android.preference.Preference findPreference(java.lang.CharSequence)";
  public String registerOnSharedPreferenceChangeListenerSubSig = "void registerOnSharedPreferenceChangeListener(android.content.SharedPreferences$OnSharedPreferenceChangeListener)";

  public String onSharedPreferenceChangedSubSig = "void onSharedPreferenceChanged(android.content.SharedPreferences,java.lang.String)";
  public String onPreferenceChangeSubSig = "boolean onPreferenceChange(android.preference.Preference,java.lang.Object)";
  public String onPreferenceClickSubSig = "boolean onPreferenceClick(android.preference.Preference)";

  // TextView.setTooltipText
  String textViewSetTooltipTextSubSig = "void setTooltipText(java.lang.CharSequence)";

  // View.setContentDescription
  String textViewSetContentDescription = "void setContentDescription(java.lang.CharSequence)";

  // view.setBackgroundResource or imageView.setImageResource
  String viewSetBackgroundResourceSubSig = "void setBackgroundResource(int)";
  String viewSetImageResourceSubSig = "void setImageResource(int)";

  public String onStartCommandSubSig = "int onStartCommand(android.content.Intent,int,int)";
  public String serviceOnCreateSubSig = "void onCreate()";

  // AsyncTask
  public String executeAsyncTaskSig = "<android.os.AsyncTask: android.os.AsyncTask execute(java.lang.Object[])>";
  public String initMethodName = "<init>";
  public String doInBackgroundAsyncTaskMethodName = "doInBackground";
  public String onPostExecuteAsyncTaskMethodName = "onPostExecute";
  public String onPreExecuteAsyncTaskMethodName = "onPreExecute";
  public String onProgressUpdateAsyncTaskMethodName = "onProgressUpdate";
  public String initSig = "void <init>()";

  public String uriParseSig = "<android.net.Uri: android.net.Uri parse(java.lang.String)>";

  public String requestRequestPermissionsSig1 = "<android.support.v4.app.ActivityCompat: void requestPermissions(android.app.Activity,java.lang.String[],int)>";
  public String requestRequestPermissionsSig2 = "<android.app.Activity: void requestPermissions(java.lang.String[],int)>";
  public String requestRequestPermissionsFragmentSig = "<android.app.Fragment: void requestPermissions(java.lang.String[],int)>";

  // Toast
  public String toastMakeTextSig1 = "<android.widget.Toast: android.widget.Toast makeText(android.content.Context,java.lang.CharSequence,int)>";
  public String toastMakeTextSig2 = "<android.widget.Toast: android.widget.Toast makeText(android.content.Context,int,int)>";
  public String toastSetTextSig1 = "<android.widget.Toast: void setText(java.lang.CharSequence)>";
  public String toastSetTextSig2 = "<android.widget.Toast: void setText(int)>";
  public String toastShowSig = "<android.widget.Toast: void show()>";

  // SnackBar
  public String snackbarMakeSig1 = "<android.support.design.widget.Snackbar: android.support.design.widget.Snackbar make(android.view.View,int,int)>";
  public String snackbarMakeSig2 = "<android.support.design.widget.Snackbar: android.support.design.widget.Snackbar make(android.view.View,java.lang.CharSequence,int)>";
  public String snackbarSetActionSig1 = "<android.support.design.widget.Snackbar: android.support.design.widget.Snackbar setAction(int,android.view.View$OnClickListener)>";
  public String snackbarSetActionSig2 = "<android.support.design.widget.Snackbar: android.support.design.widget.Snackbar setAction(java.lang.CharSequence,android.view.View$OnClickListener)>";
  public String snackbarSetTextSig1 = "<android.support.design.widget.Snackbar: android.support.design.widget.Snackbar setText(int)>";
  public String snackbarSetTextSig2 = "<android.support.design.widget.Snackbar: android.support.design.widget.Snackbar setText(java.lang.CharSequence)>";

  // DialogFragment
  public String dialogFragmentShowSig1 = "<android.app.DialogFragment: void show(android.app.FragmentManager,java.lang.String)>";
  public String dialogFragmentShowSig2 = "<android.app.DialogFragment: int show(android.app.FragmentTransaction,java.lang.String)>";
  public String dialogFragmentOnCreateDialogSubSig = "android.app.Dialog onCreateDialog(android.os.Bundle)";
}
