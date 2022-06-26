package runcode;

import java.nio.file.Paths;

public class Configs {
    public static String apkPath;
    public static String platformPath;
    public static String usrDir = System.getProperty("user.dir");
    public static String sourceSinkFile = Paths.get(usrDir, "SourcesAndSinks.txt").toString();
    public static String callBackFile = Paths.get(usrDir, "AndroidCallbacks.txt").toString();
    public static String projectDir;
    public static String dotPath;
    public static String dotPathFlowdroid;
    public static String inputCSVPath;
    public static String permissionOutput;
    public static String ic3;
    public static String dexPath;
    public static String libsPath;
    public static int callBackTimeOut;
    public static int callBackMaxDepth;

    public static void initArgs(){
        // projectDir = new File(".").getCanonicalPath();
        // projectDir = "/home/data/xiu/code-translation/code/DeepIntent";
        dotPath = Paths.get(projectDir, "data", "dot_output").toString();
        dotPathFlowdroid = Paths.get(projectDir, "data", "dot_output").toString();
        inputCSVPath = Paths.get(projectDir, "data", "inputCSVPath").toString();
        permissionOutput = Paths.get(projectDir, "data", "permissionOutput").toString();
        ic3 = Paths.get(projectDir, "data", "ic3").toString();
    }

    public static void main(String[] args){
        System.out.println(usrDir);
    }
}
