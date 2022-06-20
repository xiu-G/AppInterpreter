package runcode;

import java.util.HashSet;
import java.util.Set;

import soot.MethodOrMethodContext;
import soot.Scene;
import soot.SootMethod;
import soot.jimple.infoflow.InfoflowConfiguration;
import soot.jimple.infoflow.InfoflowConfiguration.ImplicitFlowMode;
import soot.jimple.infoflow.android.InfoflowAndroidConfiguration;
import soot.jimple.infoflow.android.SetupApplication;
import soot.jimple.toolkits.callgraph.CallGraph;
import soot.jimple.toolkits.callgraph.Edge;
import soot.options.Options;
import soot.util.dot.DotGraph;
import soot.util.queue.QueueReader;


public class Main {

    public static void parseArgs(String[] args) {
        args = new String[]{
                "-process-dir",
                "/home/data/xiu/apks/github_report/0364d434b6291ba6bcdd1cd8080615e3.apk",
                "-dex-dir",
                "/home/data/xiu/code-translation/code/runCodeComment/data/dex_dirs",
                "-android-jars",
                "/home/data/xiu/android-sdk/platforms",
                "-dot-dir",
                "/home/data/xiu/code-translation/code/runCodeComment/data/dot_result",
                "-callback-path",
                "/home/data/xiu/code-translation/code/runCodeComment/data/AndroidCallbacks.txt"
        };
        //apk path, jdk path
        for (int i=0; i < args.length; i++){
            String s = args[i];
            if("-process-dir".equals(s)){
                Configs.apkPath = args[++i];
            }else if("-android-jars".equals(s)){
                Configs.platformPath = args[++i];
            }else if("-dex-dir".equals(s)){
                Configs.dexPath = args[++i];
            }else if("-dot-path".equals(s)){
                Configs.dotPath = args[++i];
            }else if("-callback-path".equals(s)){
                Configs.callBackFile = args[++i];
            }
        }
    }

    public static void buildCallGraph() {    
        soot.G.reset(); 
        InfoflowAndroidConfiguration config = new InfoflowAndroidConfiguration();
        config.getAnalysisFileConfig().setTargetAPKFile(Configs.apkPath);
        config.getAnalysisFileConfig().setAndroidPlatformDir(Configs.platformPath);
        config.getCallbackConfig().setEnableCallbacks(true);
        config.setCallgraphAlgorithm(InfoflowConfiguration.CallgraphAlgorithm.CHA);
        config.setImplicitFlowMode(ImplicitFlowMode.AllImplicitFlows);
        config.setEnableReflection(true);
        config.setWriteOutputFiles(true);
        Options.v().set_output_dir(Configs.dexPath);
        SetupApplication analyzer = new SetupApplication(config);
        analyzer.setCallbackFile(Configs.callBackFile);
        analyzer.constructCallgraph();
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

    public static void main(String[] args) {
        parseArgs(args);
        buildCallGraph();
        // SootMethod 获取函数调用图
        CallGraph cg = Scene.v().getCallGraph();
        // 导出函数调用图
        DotGraph dot = new DotGraph("callgraph");
        analyzeCG(dot, cg);
        dot.plot(Configs.dotPath);
    }
    
}