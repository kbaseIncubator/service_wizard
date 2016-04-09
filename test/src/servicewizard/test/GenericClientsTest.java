package servicewizard.test;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.io.Writer;
import java.net.ServerSocket;
import java.net.URL;
import java.nio.file.Files;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

import junit.framework.Assert;

import org.eclipse.jetty.server.Server;
import org.eclipse.jetty.servlet.ServletContextHandler;
import org.eclipse.jetty.servlet.ServletHolder;
import org.eclipse.jetty.util.log.Log;
import org.eclipse.jetty.util.log.Logger;
import org.junit.AfterClass;
import org.junit.BeforeClass;
import org.junit.Test;

import com.fasterxml.jackson.core.type.TypeReference;

import us.kbase.auth.AuthService;
import us.kbase.auth.AuthToken;
import us.kbase.clients.GenericClient;
import us.kbase.common.service.JsonClientException;
import us.kbase.common.service.JsonServerMethod;
import us.kbase.common.service.JsonServerServlet;
import us.kbase.common.service.Tuple9;
import us.kbase.common.service.UObject;

public class GenericClientsTest {
    
    private static int serviceWizardPort = -1;
    private static Server serviceWizardServer = null;
    
    public static final String wsUrl = "https://appdev.kbase.us/services/ws";
    
    @Test
    public void testJava() throws Exception {
        GenericClient cl = new GenericClient(new URL("http://localhost:" + serviceWizardPort));
        cl.setInsecureHttpConnectionAllowed(true);
        List<Object> args = new ArrayList<Object>();
        Map<String, Object> arg1 = new LinkedHashMap<String, Object>();
        args.add(arg1);
        List<Tuple9<Long, String, String, String, Long, String, String, String, Map<String,String>>> ret = 
                cl.syncCall("Workspace.list_workspace_info", null, new TypeReference<List<
                        List<Tuple9<Long, String, String, String, Long, String, String, String, Map<String,String>>>>>() {}, false, null, args).get(0);
        for (Tuple9<Long, String, String, String, Long, String, String, String, Map<String,String>> info : ret) {
            Assert.assertTrue(info.getE2().length() > 0);
        }
    }
    
    @Test
    public void testPython() throws Exception {
        File libDir = new File("lib");
        File workDir = prepareWorkDir("python_generic_client");
        File testerFile = new File(workDir, "tester.py");
        List<String> lines = new ArrayList<String>(Arrays.asList(
                "import sys",
                "import getopt",
                "import json",
                "from kbaseclients.GenericClient import GenericClient",
                "if __name__ == \"__main__\":",
                "    client = GenericClient(url = 'http://localhost:" + serviceWizardPort + "', ignore_authrc = True)",
                "    ret = client.sync_call('Workspace.list_workspace_info', [{}])",
                "    print(json.dumps(ret))"
                ));
        writeFileLines(lines, testerFile);
        File shellFile = new File(workDir, "tester.sh");
        lines = new ArrayList<String>(Arrays.asList(
                "#!/bin/bash",
                "export PYTHONPATH=" + libDir.getCanonicalPath() + ":$PATH:$PYTHONPATH",
                "python " + testerFile.getCanonicalPath()
                ));
        writeFileLines(lines, shellFile);
        File outputFile = new File(workDir, "tester.out");
        File errorFile = new File(workDir, "tester.err");
        int exitCode = exec(workDir, outputFile, errorFile, "bash", shellFile.getCanonicalPath());
        if (exitCode == 0) {
            List<List<Tuple9<Long, String, String, String, Long, String, String, String, Map<String,String>>>> ret = 
                    UObject.getMapper().readValue(outputFile, new TypeReference<List<
                            List<Tuple9<Long, String, String, String, Long, String, String, String, Map<String,String>>>>>() {});
            for (Tuple9<Long, String, String, String, Long, String, String, String, Map<String,String>> info : ret.get(0)) {
                Assert.assertTrue(info.getE2().length() > 0);
            }
        } else {
            throw new IllegalStateException("Error running python test code: " + readText(errorFile));
        }
    }
    
    @BeforeClass
    public static void init() throws Exception {
        initSilentJettyLogger();
        serviceWizardPort = findFreePort();
        serviceWizardServer = new Server(serviceWizardPort);
        ServletContextHandler context = new ServletContextHandler(ServletContextHandler.SESSIONS);
        context.setContextPath("/");
        serviceWizardServer.setHandler(context);
        context.addServlet(new ServletHolder(new ServiceWizardMock()),"/*");
        serviceWizardServer.start();
    }
    
    @AfterClass
    public static void cleanup() throws Exception {
        if (serviceWizardServer != null)
            serviceWizardServer.stop();
    }
    
    private static AuthToken getToken() throws Exception {
        String tokenString = System.getenv("KB_AUTH_TOKEN");
        AuthToken token = null;
        if (tokenString == null) {
            String user = System.getProperty("test.user");
            String pwd = System.getProperty("test.pwd");
            token = AuthService.login(user, pwd).getToken();
        } else {
            token = new AuthToken(tokenString);
        }
        return token;
    }
    
    private static String readText(File f) throws IOException {
        StringBuilder ret = new StringBuilder();
        BufferedReader br = new BufferedReader(new FileReader(f));
        while (true) {
            String l = br.readLine();
            if (l == null)
                break;
            ret.append(l).append("\n");
        }
        br.close();
        return ret.toString();
    }

    private static int exec(File workDir, File outputFile, File errorFile, String... cmd) throws Exception {
        Process process = Runtime.getRuntime().exec(cmd, null, workDir);
        Thread outTh = readInNewThread(process.getInputStream(), outputFile);
        Thread errTh = readInNewThread(process.getErrorStream(), errorFile);
        try {
            outTh.join();
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        try {
            errTh.join();
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        return process.waitFor();
    }
    
    private static Thread readInNewThread(final InputStream is, File output) throws Exception {
        final PrintWriter pw = output == null ? null : new PrintWriter(new FileWriter(output));
        Thread ret = new Thread(new Runnable() {
            public void run() {
                try {
                    BufferedReader br = new BufferedReader(new InputStreamReader(is));
                    while (true) {
                        String line = br.readLine();
                        if (line == null)
                            break;
                        if (pw != null)
                            pw.println(line);
                    }
                    br.close();
                    pw.close();
                } catch (IOException e) {
                    e.printStackTrace();
                    throw new IllegalStateException("Error reading data from executed process", e);
                }
            }
        });
        ret.start();
        return ret;
    }

    private static File prepareWorkDir(String testName) throws IOException {
        File tempDir = new File("test_local/temp_files").getCanonicalFile();
        if (!tempDir.exists())
            tempDir.mkdirs();
        for (File dir : tempDir.listFiles()) {
            if (dir.isDirectory() && dir.getName().startsWith("test_" + testName + "_"))
                try {
                    deleteRecursively(dir);
                } catch (Exception e) {
                    System.out.println("Can not delete directory [" + dir.getName() + "]: " + e.getMessage());
                }
        }
        File workDir = new File(tempDir, "test_" + testName + "_" + System.currentTimeMillis());
        if (!workDir.exists())
            workDir.mkdir();
        return workDir;
    }

    private static void deleteRecursively(File fileOrDir) {
        if (fileOrDir.isDirectory() && !Files.isSymbolicLink(fileOrDir.toPath()))
            for (File f : fileOrDir.listFiles()) 
                deleteRecursively(f);
        fileOrDir.delete();
    }

    private static void initSilentJettyLogger() {
        Log.setLog(new Logger() {
            @Override
            public void warn(String arg0, Object arg1, Object arg2) {}
            @Override
            public void warn(String arg0, Throwable arg1) {}
            @Override
            public void warn(String arg0) {}
            @Override
            public void setDebugEnabled(boolean arg0) {}
            @Override
            public boolean isDebugEnabled() {
                return false;
            }
            @Override
            public void info(String arg0, Object arg1, Object arg2) {}
            @Override
            public void info(String arg0) {}
            @Override
            public String getName() {
                return null;
            }
            @Override
            public Logger getLogger(String arg0) {
                return this;
            }
            @Override
            public void debug(String arg0, Object arg1, Object arg2) {}
            @Override
            public void debug(String arg0, Throwable arg1) {}
            @Override
            public void debug(String arg0) {}
        });
    }

    private static int findFreePort() {
        try (ServerSocket socket = new ServerSocket(0)) {
            return socket.getLocalPort();
        } catch (IOException e) {}
        throw new IllegalStateException("Can not find available port in system");
    }

    private static void writeFileLines(List<String> lines, File targetFile) throws IOException {
        writeFileLines(lines, new FileWriter(targetFile));
    }

    private static void writeFileLines(List<String> lines, Writer targetFile) throws IOException {
        PrintWriter pw = new PrintWriter(targetFile);
        for (String l : lines)
            pw.println(l);
        pw.close();
    }
    
    public static class ServiceWizardMock extends JsonServerServlet {
        private static final long serialVersionUID = 1L;
        
        public ServiceWizardMock() {
            super("ServiceWizard");
        }
        
        @JsonServerMethod(rpc = "ServiceWizard.get_service_status")
        public Map<String, Object> getServiceStatus(Map<String, String> params) throws IOException, JsonClientException {
            String serviceName = params.get("module_name");
            Map<String, Object> ret = new LinkedHashMap<String, Object>();
            ret.put("url", wsUrl);
            return ret;
        }
    }
}
