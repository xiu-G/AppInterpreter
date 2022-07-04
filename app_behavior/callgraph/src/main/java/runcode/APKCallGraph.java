package runcode;

import java.io.*;
import java.nio.file.Paths;
import java.sql.*;
import java.util.*;
import java.util.Map.Entry;
import java.util.concurrent.CopyOnWriteArrayList;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.jgrapht.ext.ComponentNameProvider;
import org.jgrapht.ext.DOTExporter;
import org.jgrapht.graph.DirectedPseudograph;
import org.json.simple.JSONObject;
import org.xmlpull.v1.XmlPullParserException;

import soot.*;
import soot.jimple.InvokeExpr;
import soot.jimple.Stmt;
import soot.jimple.StringConstant;
import soot.jimple.AssignStmt;
import soot.jimple.infoflow.android.InfoflowAndroidConfiguration;
import soot.jimple.infoflow.android.SetupApplication;
import soot.jimple.infoflow.android.config.SootConfigForAndroid;
import soot.jimple.toolkits.callgraph.CallGraph;
import soot.options.Options;
import soot.tagkit.LineNumberTag;
import soot.util.Chain;
import soot.util.dot.DotGraph;
import soot.jimple.infoflow.InfoflowConfiguration;
import soot.jimple.infoflow.InfoflowConfiguration.ImplicitFlowMode;
import soot.jimple.toolkits.callgraph.Edge;
import soot.util.queue.QueueReader;

public class APKCallGraph {


	static DirectedPseudograph<APKCallGraph.MethodNode, CallEdge> jg = new DirectedPseudograph<>(CallEdge.class);
	static HashMap<String, APKCallGraph.MethodNode> methods = new HashMap<>();
	static HashMap<SootMethod, Boolean> visited = new HashMap<SootMethod, Boolean>();
	static ArrayList<SootMethod> methodsList = new ArrayList<>();
	static APKCallGraph apkg = new APKCallGraph();

	static ArrayList<SootMethod> handleMessageMethods = new ArrayList<>();
	static ArrayList<SootMethod> asyncExecuteMethods = new ArrayList<>();
	static ArrayList<SootMethod> clickMethods = new ArrayList<>();
	static ArrayList<SootMethod> onClickMethods = new ArrayList<>();
	static ArrayList<SootMethod> threadTgt = new ArrayList<>();
	static ArrayList<String> threadSrc = new ArrayList<>();
	static ArrayList<SootMethod> timeTaskTgt = new ArrayList<>();
	static ArrayList<String> timeTaskSrc = new ArrayList<>();

	static int edgeId = 0;
	static int nodeId = 0;
	static boolean isGenerated = false;


	static IC3ProtobufParser ic3parser = new IC3ProtobufParser();



	static HashMap<String, List<String>> edges = new HashMap<>();
	static HashMap<String, List<String>> afterICC = new HashMap<>();

	//static Connection connection = null;
	static HashMap<String, ArrayList<String>> lineVSHdl = new HashMap<>();
	static HashMap<String, SootMethod> methodKey = new HashMap<>();
	static HashMap<String, ArrayList<String>> methodsClass = new HashMap<>();
	static HashMap<String, ArrayList<String>> HdlVSPM = new HashMap<>();
	static HashMap<String, ArrayList<String>> permMethods = new HashMap<>();
	static ArrayList<String> handlers = new ArrayList<>();
	static HashMap<String, ArrayList<Stmt>> methodToStmts = new HashMap<>();
	static HashMap<String, ArrayList<String>> startActivity = new HashMap<>();
	static HashMap<String, ArrayList<String>> stringLists = new HashMap<>();


	class MethodNode {
		SootMethod m;
		String signature;
		public int id;

		public MethodNode(SootMethod m, int id) {
			this.m = m;

			if (m != null) {
				signature = m.getSignature();
			}
			this.id = id;
		}

		public MethodNode(String name, int id){
			this.signature = name;
			this.id = id;
		}

		public String getSignature() {
			return signature;
		}

		@Override
		public int hashCode() {
			final int prime = 31;
			int result = 1;
			result = prime * result + getOuterType().hashCode();
			result = prime * result + ((signature == null) ? 0 : signature.hashCode());
			return result;
		}

		@Override
		public boolean equals(Object obj) {
			if (this == obj)
				return true;
			if (obj == null)
				return false;
			if (getClass() != obj.getClass())
				return false;
			MethodNode other = (MethodNode) obj;
			if (!getOuterType().equals(other.getOuterType()))
				return false;
			if (signature == null) {
				if (other.signature != null)
					return false;
			} else if (!signature.equals(other.signature))
				return false;
			return true;
		}

		private APKCallGraph getOuterType() {
			return APKCallGraph.this;
		}

	}

	class CallEdge {
		private MethodNode source;
		private MethodNode target;
		private int id;

		public MethodNode getSource() {
			return source;
		}

		public void setSource(MethodNode source) {
			this.source = source;
		}

		public MethodNode getTarget() {
			return target;
		}

		public void setTarget(MethodNode target) {
			this.target = target;
		}

		public int getId() {
			return id;
		}

		public void setId(int id) {
			this.id = id;
		}

		public CallEdge(MethodNode source, MethodNode target, int id) {
			super();
			this.source = source;
			this.target = target;
			this.id = id;
		}

	}

	class MethodNodeNameProvider implements ComponentNameProvider<MethodNode> {

		@Override
		public String getName(MethodNode e) {
			return e.getSignature();
		}

	}

	class CallEdgeLabelProvider implements ComponentNameProvider<CallEdge> {

		@Override
		public String getName(CallEdge e) {
			return e.toString();
		}

	}

	class MethodnodeIdProvider implements ComponentNameProvider<MethodNode> {
		@Override
		public String getName(MethodNode e) {
			return "" + e.id;
		}

	}


	public static void main(String[] args) throws Exception {
		/*
		 * Main function, basic running configs, change dir(s) before running.
		 * Scan every input widget-handler mapping, skip when no mapping is found.
		 * If mapping is found, build extended static call graph of the app, extract subgraph(s), check API(s) and permission.
		 */
		// args = new String[]{
		// 	// "/home/data/xiu/code-translation/code/guibat/apk/com.voicenotebook.voicenotebook.apk",
		// 	// "/home/data/xiu/code-translation/code/guibat/apk",
		// 	"/home/data/yuec/DeepIntent/data/example/malicious/net.lazyer.wiyun.ppl.yxjd.apk",
		// 	"/home/data/yuec/DeepIntent/data/example/malicious",
		// 	"data/img2widgets/", //inputCSVPath
		// 	"data/permission_output/", //permissionOutput
		// 	"data/ic3_output/", //ic3Output
		// 	"29",
		// 	"/home/data/xiu/android-sdk/platforms",
		// };
		// args = new String[]{
		// 	"/home/data/yuec/DeepIntent/data/example/benign/1311833082_net.lepeng.batterydoctor.apk",
		// 	"/home/data/yuec/DeepIntent/data/example/benign",
		// 	"/home/data/xiu/code-translation/code/DeepIntent/data/img2widgets/", //inputCSVPath
		// 	"/home/data/xiu/code-translation/code/DeepIntent/data/permission_output/", //permissionOutput
		// 	"/home/data/xiu/code-translation/code/DeepIntent/data/ic3_output/", //ic3Output
		// 	"18",
		// 	"/home/data/xiu/android-sdk/platforms",
		// 	"/home/data/xiu/code-translation/code/DeepIntent/data/decode_dir",
		// };
		File tmpFile=new File(args[0]);
		String apk=tmpFile.getName().substring(0, tmpFile.getName().indexOf(".apk"));
		// String apk = "com.Abby_Alex";
		// String apk = args[0].substring(args[0].lastIndexOf("/"), args[0].indexOf(".apk"));
		Configs.apkPath = args[1];
		String inputCSVPath = args[2];
		// String inputCSVPath = "/Users/shaoyang/Desktop/";
		// String inputCSVPath = Configs.inputCSVPath;
		String permissionOutput = args[3];
		// String permissionOutput = "/Users/shaoyang/Desktop/";
		//String apk = "nextcloud";
		String ic3 = args[4];
		// String ic3 = "/Users/shaoyang/Desktop/ic3output/";
		Configs.initArgs();
		String api_level = args[5];
		Configs.platformPath = args[6];
		System.out.println("Start analyze apk: " + apk + ".apk");

		// String apkPath = appPath + apk + ".apk";
		String apkPath = args[0];
		Configs.apkPath = apkPath;

		int numberOfLines = 0;
		boolean hasHandler = false;
		String inputCSV = apk + "_img2widgets.csv";
		File file = new File(Paths.get(inputCSVPath, inputCSV).toString());
		FileInputStream fis = new FileInputStream(file);
		Scanner scanner = new Scanner(fis);
		while(scanner.hasNextLine()){
			String line = scanner.nextLine();
			int front = line.indexOf("[");
			int back = line.indexOf("]");
			if ((back - front) > 1){
				hasHandler = true;
				numberOfLines ++;
				break;
			}else {
				hasHandler = false;
			}
			numberOfLines ++;
		}

		if (numberOfLines == 1){
			generateCallGraph(apk, apkPath, ic3, api_level);
			System.out.println("No widget found.");
		}else if (numberOfLines > 1 && hasHandler != true) {
			generateCallGraph(apk, apkPath, ic3, api_level);
			System.out.println("No handler found.");
		}else {
			generateCallGraph(apk, apkPath, ic3, api_level);
			getHandlers(apk,inputCSVPath + inputCSV);
			if (permMethods.size() > 0){
				writeInfoToFile(permissionOutput, apk);
			}
		}
		scanner.close();
	}

	    /**
     * Iterate over the call Graph by visit edges one by one.
     * @param dot dot instance to create a dot file
     * @param cg call graph
     */
    public static void analyzeCG(DotGraph dot, CallGraph cg) {
        QueueReader<Edge> edges = cg.listener();
        Set<String> visited = new HashSet<>();
        // iterate over edges of the call graph
        while (edges.hasNext()) {
            Edge edge = edges.next();
            SootMethod target = (SootMethod) edge.getTgt();
            MethodOrMethodContext src = edge.getSrc();
            if (!visited.contains(src.toString())) {
                dot.drawNode(src.toString());
                visited.add(src.toString());
            }
            if (!visited.contains(target.toString())) {
                dot.drawNode(target.toString());
                visited.add(target.toString());
            }

            dot.drawEdge(src.toString(), target.toString());
        }
        System.out.println(cg.size());
    }

	public static void generateCallGraph(String apk, String apkPath, String ic3, String api_level) throws IOException, XmlPullParserException {
		/*
		 * Soot configs
		 * Running BFS to build call graph
		 * Integrate multi-threading methods, callbacks, ICC and so on.
		 */
		soot.G.reset();
        InfoflowAndroidConfiguration config = new InfoflowAndroidConfiguration();
        config.getAnalysisFileConfig().setTargetAPKFile(Configs.apkPath);
        config.getAnalysisFileConfig().setAndroidPlatformDir(Configs.platformPath);
        config.getCallbackConfig().setEnableCallbacks(true);
        config.setCallgraphAlgorithm(InfoflowConfiguration.CallgraphAlgorithm.CHA);
        config.setImplicitFlowMode(ImplicitFlowMode.AllImplicitFlows);
        config.setEnableReflection(true);
        config.setWriteOutputFiles(true);
		config.getCallbackConfig().setMaxAnalysisCallbackDepth(350);
        SetupApplication analyzer = new SetupApplication(config);
		SootConfigForAndroid sootConf = new SootConfigForAndroid() {
            @Override
            public void setSootOptions(Options options, InfoflowConfiguration config) {
                super.setSootOptions(options, config);
                // Options.v().set_output_dir(Configs.dexPath);
				Options.v().set_android_api_version(Integer.valueOf(api_level));
				Options.v().set_process_multiple_dex(true);
				Options.v().set_keep_line_number(true);
				Options.v().set_process_dir(Collections.singletonList(apkPath));
				Options.v().set_src_prec(Options.src_prec_apk);
				Options.v().setPhaseOption("cg.spark", "on");
				Options.v().setPhaseOption("cg.cha", "enabled:true");
				Options.v().setPhaseOption("cg", "all-reachable:true");
				Options.v().set_allow_phantom_refs(true);
				Options.v().set_no_writeout_body_releasing(true);
				Options.v().set_output_format(Options.output_format_jimple);
				Options.v().set_whole_program(true);
				PhaseOptions.v().setPhaseOption("tag.ln", "on");
            }
        };
		analyzer.setSootConfig(sootConf);
        analyzer.setCallbackFile(Configs.callBackFile);
        analyzer.constructCallgraph();
		// CallGraph cg = Scene.v().getCallGraph();
        // // 导出函数调用图
        // DotGraph dot = new DotGraph("callgraph");
        // analyzeCG(dot, cg);
        // dot.plot(Configs.dotPathFlowdroid);
		Chain<SootClass> applicationClasses = Scene.v().getApplicationClasses();
		for (SootClass sootClass : applicationClasses) {

			List<SootMethod> ms = sootClass.getMethods();
			for (SootMethod m : ms) {
				ArrayList<String> temp = new ArrayList<>();
				if (methodsClass.containsKey(m) == false){
					temp.add(sootClass.getName());
					methodsClass.put(m.getSignature(), temp);
				}else{
					methodsClass.get(m.getSignature()).add(sootClass.getName());
				}
				if (methodsList.contains(m)) {
					continue;
				}
				methodsList.add(m);
			}
		}

		CopyOnWriteArrayList<SootMethod> list = new CopyOnWriteArrayList<>(methodsList);

		while (list.size() > 0){
			if (!methodKey.containsKey(list.get(0).getSignature().toString())){
				methodKey.put(list.get(0).getSignature().toString(), list.get(0));
			}

			if (visited.containsKey(list.get(0)) == false){
				if (!list.get(0).hasActiveBody()){
					list.remove(list.get(0));
					continue;
				}

				Body body = list.get(0).retrieveActiveBody();
				Iterator<Unit> stmts = body.getUnits().iterator();
				visited.put(list.get(0), true);
				while (stmts.hasNext()) {
					Stmt s = (Stmt) stmts.next(); 
					if (s.toString().contains("\"")){
						// String tmpS = assign.getRightOp().toString();
						String tmpS = s.toString().substring(s.toString().indexOf("\""), s.toString().lastIndexOf("\"")+1);
						if (!stringLists.containsKey(tmpS)){
							ArrayList<String> temp = new ArrayList<>();
								temp.add(list.get(0).getSignature().toString());
								stringLists.put(tmpS, temp);	
						}else{
							if (!stringLists.get(tmpS).contains(list.get(0).getSignature().toString())){
								stringLists.get(tmpS).add(list.get(0).getSignature().toString());
							}
							
						}
					}
					if (s.toString().contains("invoke")) {
						if (list.get(0).getSignature().contains("void handleMessage(android.os.Message)>")){
							if (!handleMessageMethods.contains(list.get(0))){
								handleMessageMethods.add(list.get(0));
							}
						}

						if ((list.get(0).getSignature().contains("doInBackground(")) ||
								(list.get(0).getSignature().contains("onPreExecute(")) ||
								(list.get(0).getSignature().contains("onPostExecute("))){
							if (!asyncExecuteMethods.contains(list.get(0))){
								asyncExecuteMethods.add(list.get(0));
							}
						}
						if (list.get(0).getSignature().contains(": void onClick(")){
							if (!clickMethods.contains(list.get(0))){
								clickMethods.add(list.get(0));
							}
						}
						if (list.get(0).getSignature().contains("setOnClickListener(")){
							if (!onClickMethods.contains(list.get(0))){
								onClickMethods.add(list.get(0));
							}
						}
						if (list.get(0).getSignature().contains(": void run()")){
							if (list.get(0).getDeclaringClass().getSuperclass().toString().contains("java.lang.Thread") ||
						list.get(0).getDeclaringClass().getInterfaces().toString().contains("java.lang.Runnable")){
								if (!threadTgt.contains(list.get(0))){
									threadTgt.add(list.get(0));
									String src = "<" + list.get(0).getDeclaringClass().toString() + ": void start()>";
									if (!threadSrc.contains(src)){
										threadSrc.add(src);
									}
								}
							}
							if (list.get(0).getDeclaringClass().getSuperclass().toString().contains("java.util.TimerTask")){
								timeTaskTgt.add(list.get(0));
							}
						}

						try{
							InvokeExpr expr = s.getInvokeExpr();
							if (expr.getMethod().getSignature().contains("void schedule")){
								timeTaskSrc.add(expr.getMethod().getSignature());
							}
							if (expr.getMethod().getSignature().contains("<android.content.Intent: void <init>")){
								try{
									String srcMethod = list.get(0).getSignature();
									String tarActivity = s.getInvokeExprBox().getValue().getUseBoxes().get(1).getValue().toString();
									if (tarActivity.startsWith("class ")){
										tarActivity = tarActivity.split("class ")[1].replace("/", ".");
										if (tarActivity.startsWith("\"L")){
											tarActivity = tarActivity.substring(2, tarActivity.length()-2);
										}else{
											tarActivity = tarActivity.substring(1, tarActivity.length()-1);
										}

									}else{
										tarActivity = "";
									}
									if (!startActivity.containsKey(srcMethod)){
										ArrayList<String> temp = new ArrayList<>();
										temp.add(tarActivity);
										startActivity.put(srcMethod, temp);
									}else{
										startActivity.get(srcMethod).add(tarActivity);
									}
								}catch(Exception e){
									System.out.println("Intent Error!");
								}
							}

							if (!edges.containsKey(list.get(0).getSignature())){
								List<String> temp = new ArrayList<>();
								if (expr.getMethod().getDeclaringClass().toString() == "java.lang.Thread"){
									temp.add(expr.getMethodRef().getSignature());
								}else {
									temp.add(expr.getMethod().getSignature());
								}

								edges.put(list.get(0).getSignature(), temp);
							}else if (!edges.get(list.get(0).getSignature()).contains(expr.getMethodRef().getSignature())){
								edges.get(list.get(0).getSignature()).add(expr.getMethodRef().getSignature());
							}

							methodsList.add(expr.getMethod());
							list.add(expr.getMethod());
							String key = expr.getMethod().getSignature();
							if (methodsClass.containsKey(key)){
								for (String sootClass : methodsClass.get(list.get(0).getSignature())) {
									if (methodsClass.get(key).contains(sootClass) == false){
										methodsClass.get(key).add(sootClass);
									}
								}
							}else{
								ArrayList<String> temp = new ArrayList<>();
								for (String item : methodsClass.get(list.get(0).getSignature())){
									temp.add(item);
								}
								methodsClass.put(key, temp);
							}
							if (methodToStmts.get(expr.getMethod()) != null){
								methodToStmts.get(expr.getMethod()).add(s);
							}
							else{
								ArrayList<Stmt> temp = new ArrayList<>();
								temp.add(s);
								methodToStmts.put(expr.getMethod().getSignature(), temp);
							}
						}catch (Exception e){
							System.out.println("getInvokeExpr() called with no invokeExpr present!");
						}
					}
					
				}

			}
			list.remove(list.get(0));
		}


		for (String src: edges.keySet()){
			for (String tgt: edges.get(src)){
				edgeId++;

				if (!methods.containsKey(src)) {
					nodeId++;
					methods.put(src, apkg.new MethodNode(src, nodeId));
					jg.addVertex(methods.get(src));
				}

				if (!methods.containsKey(tgt)) {
					nodeId++;
					methods.put(tgt, apkg.new MethodNode(tgt, nodeId));
					jg.addVertex(methods.get(tgt));
				}
				MethodNode srcNode = methods.get(src);
				MethodNode tgtNode = methods.get(tgt);

				jg.addEdge(srcNode, tgtNode, apkg.new CallEdge(srcNode, tgtNode, edgeId));
			}
		}


		boolean useic3 = true;
		int lenguri = 0;
		if (useic3) {
			File ic3folder = new File(Paths.get(ic3, apk).toString());
			File[] listFiles = ic3folder.listFiles();
			if (listFiles == null) {
				System.out.println(Paths.get(ic3, apk).toString() + " is null. ");
			}
			ArrayList<String> finishedMethods = new ArrayList<String>();
			if (listFiles != null && listFiles.length > 0) {
				for (File listfile : listFiles) {
					HashMap<String, HashSet<String>> m2providers = new HashMap<>();
					HashMap<String, HashSet<String>> m2intents = new HashMap<>();
					HashMap<String, HashSet<String>> m2extra = new HashMap<>();
					HashMap<String, ArrayList<String>> iccs = ic3parser.parseFromFile(listfile.getAbsolutePath(),
							m2providers, m2intents, m2extra);

					// for service class, you should add an edge from a method
					for (Entry<String, ArrayList<String>> icc : iccs.entrySet()) {
						String fromMethod = icc.getKey();
						ArrayList<String> toClasses = icc.getValue();
						MethodNode from = methods.get(fromMethod);
						if (startActivity.containsKey(from.getSignature())){
							finishedMethods.add(from.getSignature());
							ArrayList<String> tmpClasses = startActivity.get(from.getSignature());
							if(tmpClasses != null){
								for (String tmpClass: tmpClasses){
									if (!toClasses.contains(tmpClass)){
										icc.getValue().add(tmpClass);
									}
								}
							}
						}
					}
					for (String methodTmp: startActivity.keySet()){
						if (!finishedMethods.contains(methodTmp)){
							iccs.put(methodTmp, startActivity.get(methodTmp));
						}
					}
					for (Entry<String, ArrayList<String>> icc : iccs.entrySet()) {
						String fromMethod = icc.getKey();
						ArrayList<String> toClasses = icc.getValue();
						HashSet<String> actions = new HashSet<String>();
						HashSet<String> uris = new HashSet<String>();
						HashSet<String> extras = new HashSet<String>();
						if (!methods.containsKey(fromMethod)) {
							System.out.println("error finding from method: " + fromMethod);
							continue;
						}
						if (m2intents.containsKey(fromMethod)){
							actions = m2intents.get(fromMethod);
						}
						if (m2providers.containsKey(fromMethod)){
							uris = m2providers.get(fromMethod);
						}
						if (m2extra.containsKey(fromMethod)){
							extras = m2extra.get(fromMethod);
						}
						MethodNode from = methods.get(fromMethod);
						for (String clazz : toClasses) {
							if (clazz.length() == 0) {
								// System.out.println("empty clazz");
								continue;
							}
							try{
								SootClass loadClass = Scene.v().loadClassAndSupport(clazz);

								List<SootMethod> loadMethods = loadClass.getMethods();
								for (SootMethod loadMethod : loadMethods) {
									if (loadMethod.getName().startsWith("onCreate")
											|| loadMethod.getName().startsWith("onStart")) {
										if (!methods.containsKey(loadMethod.getSignature())) {
											nodeId++;
											methods.put(loadMethod.getSignature(), apkg.new MethodNode(loadMethod, nodeId));
											jg.addVertex(methods.get(loadMethod.getSignature()));
										}

										edgeId++;
										MethodNode to = methods.get(loadMethod.getSignature());
										jg.addEdge(from, to, apkg.new CallEdge(from, to, edgeId)); //add by me
									}
								}

							}catch (Exception e){
								System.out.println("clazz in ic3 cannot be loaded!");
							}

						}
						for (String src: edges.get(fromMethod)){
							System.out.println(src);
							if (!src.contains(": void startActivity(")){
								continue;
							}else{
								String tgt = "<" + iccs.get(fromMethod).get(0) + ": void onCreate(android.os.Bundle)>";
								if (jg.containsVertex(methods.get(tgt)) == true){
									if (afterICC.containsKey(fromMethod) == false) {
										List<String> temp = new ArrayList<>();
										temp.add(src);
										temp.add(tgt);
										afterICC.put(fromMethod, temp);
									}
									if (edges.containsKey(src)){
										edges.get(src).add(tgt);
									}else{
										List<String> temp = new ArrayList<>();
										temp.add(tgt);
										edges.put(src, temp);
									}
									jg.addEdge(methods.get(src), methods.get(tgt), apkg.new CallEdge(methods.get(src), methods.get(tgt), edgeId++));
								}else{
									continue;
								}
							}
						}

						for (String action: actions){
							action = "<android.addextras."+action+": void <init>()>";
							if (!methods.containsKey(action)){
								nodeId++;
								methods.put(action, apkg.new MethodNode(action, nodeId));
								jg.addVertex(methods.get(action));
							}
							edgeId++;
							MethodNode to = methods.get(action);
							jg.addEdge(from, to, apkg.new CallEdge(from, to, edgeId)); //add by me
						}

						for (String uri: uris){
							String tmpURI = "";
							try{
								lenguri += 1;
								tmpURI = "<android.addextras."+uri.split("content://")[1].replace("/", "_") + ": void <init>()>";
							}catch (Exception e) {
								continue;
							}
							if (!methods.containsKey(tmpURI)){
								nodeId++;
								methods.put(tmpURI, apkg.new MethodNode(tmpURI, nodeId));
								jg.addVertex(methods.get(tmpURI));
							}
							edgeId++;
							MethodNode to = methods.get(tmpURI);
							jg.addEdge(from, to, apkg.new CallEdge(from, to, edgeId)); //add by me
						}
						for (String extra: extras){
							extra = "<android.addextras."+extra+": void <init>()>";
							if (!methods.containsKey(extra)){
								nodeId++;
								methods.put(extra, apkg.new MethodNode(extra, nodeId));
								jg.addVertex(methods.get(extra));
							}
							edgeId++;
							MethodNode to = methods.get(extra);
							jg.addEdge(from, to, apkg.new CallEdge(from, to, edgeId)); //add by me
						}
					}
				}
			}
		}
		for (String m: methods.keySet()){
			connectThread(m);
			connectSendMessage(m);
			connectAsyncExecute(m);
			connectClickCall(m);
			connectTimer(m);
		}


		DOTExporter<MethodNode, CallEdge> exporter = new DOTExporter<MethodNode, CallEdge>(
				apkg.new MethodnodeIdProvider(), apkg.new MethodNodeNameProvider(), null);
		// File file = new File("/Users/shaoyang/Downloads/Static_Analysis/dot_output/" + apk + "/");
		File file = new File(Paths.get(Configs.dotPath, apk).toString());
		file.mkdir();
		exporter.exportGraph(jg, new FileWriter(Paths.get(Configs.dotPath, apk, apk+".dot").toString()));
		writeStringList(apk);
		
	}

	public static void writeStringList(String apk) throws IOException{
		File file = new File(Paths.get(Configs.stringPath, apk+".json").toString());
		BufferedWriter bw = new BufferedWriter(new FileWriter(file, false));
		JSONObject jsonObject = new JSONObject(stringLists);
		bw.write(jsonObject.toJSONString());   
		bw.close();   
		// s.writeObject(stringLists);
		// s.flush();
		// s.close();
    }


	 public static void connectThread(String src){
		if (threadSrc.contains(src)){
			MethodNode srcNode = methods.get(src);
			int i = src.indexOf(":");
			for (SootMethod tgt: threadTgt){
				if (tgt.getSignature().contains(src.substring(0,i)) || src.contains("<java.lang.Thread")){
					MethodNode tgtNode = methods.get(tgt.getSignature());
					if (edges.containsKey(src)){
						edges.get(src).add(tgt.getSignature());
					}else{
						List<String> temp = new ArrayList<>();
						temp.add(tgt.getSignature());
						edges.put(src, temp);
					}
					jg.addEdge(srcNode, tgtNode, apkg.new CallEdge(srcNode, tgtNode, edgeId++));
				}
			}
			System.out.println("Connect thread successful");
		}
	 }

	 public static void connectClickCall(String  src){
		if (src.contains(": void setOnClickListener(")){
			for (SootMethod tgt: clickMethods){
				List<String> tgtClass= methodsClass.get(tgt.getSignature());
				for (String sootClass: tgtClass){
                    if (!methodsClass.containsKey(src)){
                        continue;
                    }
					if (methodsClass.get(src).contains(sootClass) || methodsClass.get(src).contains(sootClass.split("\\$")[0])){
						MethodNode srcNode = methods.get(src);
						MethodNode tgtNode = methods.get(tgt.getSignature());
						if (edges.containsKey(src)){
							edges.get(src).add(tgt.getSignature());
						}else{
							List<String> temp = new ArrayList<>();
							temp.add(tgt.getSignature());
							edges.put(src, temp);
						}
						jg.addEdge(srcNode, tgtNode, apkg.new CallEdge(srcNode, tgtNode, edgeId++));
						break;
					}
				}
			}
			System.out.println("Connect click calls successful");
		}
	 }

	 public static void connectSendMessage(String src){
		if (src.contains("boolean sendMessage(android.os.Message)>")){
			for (SootMethod tgt: handleMessageMethods){
				MethodNode srcNode = methods.get(src);
				MethodNode tgtNode = methods.get(tgt.getSignature());
				if (edges.containsKey(src)){
					edges.get(src).add(tgt.getSignature());
				}else{
					List<String> temp = new ArrayList<>();
					temp.add(tgt.getSignature());
					edges.put(src, temp);
				}
				jg.addEdge(srcNode, tgtNode, apkg.new CallEdge(srcNode, tgtNode, edgeId++));
			}
			System.out.println("Connect message calls successful");
		}
	 }

	 public static void connectAsyncExecute(String src){
		if ((src.contains("android.os.AsyncTask execute(java.lang.Object[])>")) || src.contains("AsyncTask executeOnExecutor(")){
			for (SootMethod tgt: asyncExecuteMethods){
                List<String> tgtClass= methodsClass.get(tgt.getSignature());

                if (!methodsClass.containsKey(src)){
                    continue;
                }
                for (String sootClass: tgtClass){
                    if (methodsClass.get(src).contains(sootClass) || methodsClass.get(src).contains(sootClass.split("\\$")[0])){
                        MethodNode srcNode = methods.get(src);
				        MethodNode tgtNode = methods.get(tgt.getSignature());

                        if (edges.containsKey(src)){
                            edges.get(src).add(tgt.getSignature());
                        }else{
                            List<String> temp = new ArrayList<>();
                            temp.add(tgt.getSignature());
                            edges.put(src, temp);
                        }
                        jg.addEdge(srcNode, tgtNode, apkg.new CallEdge(srcNode, tgtNode, edgeId++));

                    }
                }
			}
			System.out.println("Connect asynctask calls successful");
		}
	 }

	 public static void connectTimer(String src){
		if (timeTaskSrc.contains(src)){
			MethodNode srcNode = methods.get(src);
			for (SootMethod tgt: timeTaskTgt){
				List<String> tgtClass= methodsClass.get(tgt.getSignature());
				for (String sootClass: tgtClass){
					if (methodsClass.get(src).contains(sootClass) || methodsClass.get(src).contains(sootClass.split("\\$")[0])){
						MethodNode tgtNode = methods.get(tgt.getSignature());
						if (edges.containsKey(src)){
							edges.get(src).add(tgt.getSignature());
						}else{
							List<String> temp = new ArrayList<>();
							temp.add(tgt.getSignature());
							edges.put(src, temp);
						}
						jg.addEdge(srcNode, tgtNode, apkg.new CallEdge(srcNode, tgtNode, edgeId++));
						break;
					}
				}
			}
			System.out.println("Connect timer successful");
		}
	 }

	 public static void generateSubGraphOfMethod(String apk, String method) throws IOException, SQLException {
		/*
		 * This function is used to generate subgraph of an event handler.
		 * Each node in the subgraph will be checked if it is related to certain permissions.
		 */
		DirectedPseudograph<APKCallGraph.MethodNode, CallEdge> subGraph = new DirectedPseudograph<>(CallEdge.class);

		ArrayList<String> subgraph = new ArrayList<>();
		if(!methods.containsKey(method)){
			System.out.println("Method not found, please enter again!");
		}else {
			HashMap<String, Boolean> hasVisited = new HashMap<>();
			List<String> list = new ArrayList<>();
			list.add(method);
			hasVisited.put(method, true);
			while (list.size() > 0) {
				if (edges.get(list.get(0)) == null){
					list.remove(list.get(0));
					continue;
				}

				for (String tgt: edges.get(list.get(0))){
					if (list.get(0).contains(": void startActivity(")){
						if (afterICC.get(method) == null){
							continue;
						}
					}
					//System.out.println(tgt);
					if (!subGraph.containsVertex(methods.get(list.get(0)))){
						subGraph.addVertex(methods.get(list.get(0)));
					}
					if (!subGraph.containsVertex(methods.get(tgt))){
						subGraph.addVertex(methods.get(tgt));
					}
					subGraph.addEdge(methods.get(list.get(0)), methods.get(tgt), apkg.new CallEdge(methods.get(list.get(0)), methods.get(tgt), edgeId++));

					if (hasVisited.containsKey(tgt)){
						continue;
					}
					hasVisited.put(tgt, true);
					list.add(tgt);
					subgraph.add(tgt);
				}
				list.remove(list.get(0));
			}


			DOTExporter<MethodNode, CallEdge> exporter = new DOTExporter<MethodNode, CallEdge>(
					apkg.new MethodnodeIdProvider(), apkg.new MethodNodeNameProvider(), null);
			// exporter.exportGraph(subGraph, new FileWriter("/Users/shaoyang/Downloads/Static_Analysis/dot_output/" + apk + "/" + method + ".dot"));
			exporter.exportGraph(subGraph, new FileWriter(Paths.get(Configs.dotPath, apk, method+".dot").toString()));
			isGenerated = true;

		}
		System.out.println("Handler---------------" + method);
		System.out.println(".....................................................");
		for (String m: subgraph){
			// System.out.println("Checking permissions");
			// System.out.println("Method----------------" + m);
			String permission = getPermission(m.replace("\'", ""));
			if (permission == null){
				continue;
			}
			else {
				if (HdlVSPM.get(method) == null){
					ArrayList<String> temp = new ArrayList<>();
					temp.add(permission);
					HdlVSPM.put(method, temp);
				}
				else{
					HdlVSPM.get(method).add(permission);
				}
			}
			if (permMethods.get(m) == null){
				ArrayList<String> permissions = new ArrayList<>();
				permissions.add(permission);
				permMethods.put(m, permissions);
			}
		}
	 }

	public static String getPermission(String method) throws SQLException{
		/*
		 * Connect mysql PScout mapping database.
		 * Run sql given certain APIs, and return corresponding permissions.
		 */
		Connection connection = null;

		String permission = null;
		String methodClass = method.substring(1, method.indexOf(":"));
		String sql = "select Permission from outputmapping where Method = '" + method + "'";
		String driver = "com.mysql.cj.jdbc.Driver";
		// String url = "jdbc:mysql://localhost:3306/APKCalls?user=root&password=jiaozhuys05311&serverTimezone=GMT";
		// String url = "jdbc:mysql://localhost:3306/cc?user=codecomment&password=test123456&serverTimezone=GMT";
		String url = "jdbc:mysql://localhost:3306/cc?user=codecomment&password=test123456&serverTimezone=UTC&useSSL=false";
		try {
			Class.forName(driver);
			connection = DriverManager.getConnection(url);
			Statement stmt = connection.createStatement();
			ResultSet resultSet = stmt.executeQuery(sql);
			if (resultSet.next() == true){
				permission = resultSet.getString(1);
			}
		} catch (ClassNotFoundException e) {
			e.printStackTrace();
		}
		connection.close();
		return permission;
	}


	public static void getHandlers(String apk, String fileName) throws IOException, SQLException {
		/*
		 * Using regex to match event handlers.
		 * If handler is found, it is used to generate subgraph.
		 */
		System.out.println("Processing file :" + fileName);
		try {
			String regex = "<(.*?)>";
			FileReader f_reader = new FileReader(fileName);
			BufferedReader br = new BufferedReader(f_reader);
			String line = "";
			while ((line = br.readLine()) != null){
				String tempLine = "";
				Pattern pattern = Pattern.compile(regex);
				Matcher matcher = pattern.matcher(line);
				while (matcher.find()){
					tempLine = line.substring(0, line.indexOf("["));
					if (handlers.contains(matcher.group(1))){
						if (!lineVSHdl.containsKey(tempLine)){
							ArrayList<String> temp = new ArrayList<>();
							temp.add("<" + matcher.group(1) + ">");
							lineVSHdl.put(tempLine, temp);
							continue;
						}else{
							lineVSHdl.get(tempLine).add("<" + matcher.group(1) + ">");
							continue;
						}
					}
					handlers.add(matcher.group(1));
					//System.out.println(line);
					if (lineVSHdl.containsKey(tempLine) == false){
						ArrayList<String> temp = new ArrayList<>();
						temp.add("<" + matcher.group(1) + ">");
						lineVSHdl.put(tempLine, temp);
						generateSubGraphOfMethod( apk, "<" + matcher.group(1) + ">");
					}else {
						lineVSHdl.get(tempLine).add("<" + matcher.group(1) + ">");
						generateSubGraphOfMethod( apk, "<" + matcher.group(1) + ">");
					}
				}
			}
		}catch (Exception e){
			System.out.println(e.toString());
		}
	}

	public static void writeInfoToFile(String permissionOutput, String apkName) throws IOException {
		File file = new File(permissionOutput + apkName + "_permission.csv");
		if (file.exists() == false){
			file.createNewFile();
		}
		FileWriter f_writer = new FileWriter(file);
		BufferedWriter bw = new BufferedWriter(f_writer);
		bw.write("APK\tImage\tWID\tWID Name\tLayout\tHandler\tMethod\tLines\tPermissions\n");
		for (String line: lineVSHdl.keySet()){
			for (String handler: HdlVSPM.keySet()){
				if (!lineVSHdl.get(line).contains(handler)){
					continue;
				}
				for (String method: permMethods.keySet()){
					for (SootMethod m: methodsList){
						if (m.toString() == method){
							ArrayList<Stmt> stmts = methodToStmts.get(m.getSignature());
							ArrayList<String> lineNums = new ArrayList<>();
							for (Stmt s: stmts){
								Unit u = (Unit)s;
								LineNumberTag tag = (LineNumberTag)u.getTag("LineNumberTag");
								try {
									lineNums.add(String.valueOf(tag.getLineNumber()));
								} catch (Exception e) {
									bw.close();
									return;
								}
							}
							bw.write(line  + handler + "\t" +
									method + "\t" +
									lineNums + "\t" +
									permMethods.get(method) + "\n");

						}
						else{
							continue;
						}
					}
				}
			}
		}
		bw.close();
	}
}
