/*
 * WTGDemoClient.java - part of the GATOR project
 *
 * Copyright (c) 2018 The Ohio State University
 *
 * This file is distributed under the terms described in LICENSE in the
 * root directory.
 */

package presto.android.gui.clients;

import presto.android.Configs;
import presto.android.Debug;
import presto.android.Logger;
import presto.android.gui.GUIAnalysisClient;
import presto.android.gui.GUIAnalysisOutput;
import presto.android.gui.clients.energy.VarUtil;
import presto.android.gui.graph.NIdNode;
import presto.android.gui.graph.NObjectNode;
import presto.android.gui.wtg.EventHandler;
import presto.android.gui.wtg.StackOperation;
import presto.android.gui.wtg.WTGAnalysisOutput;
import presto.android.gui.wtg.WTGBuilder;
import presto.android.gui.wtg.ds.HandlerBean;
import presto.android.gui.wtg.ds.WTG;
import presto.android.gui.wtg.ds.WTGEdge;
import presto.android.gui.wtg.ds.WTGNode;
import soot.SootMethod;

import java.io.File;
import java.io.PrintWriter;
import java.nio.file.Paths;
import java.util.Collection;
import java.util.Map;
import java.util.Set;

import org.json.simple.JSONArray;
import org.json.simple.JSONObject;

import com.google.common.collect.Multimap;

/**
 * Created by zero on 10/21/15.
 */
public class WTGDemoClient implements GUIAnalysisClient {
  @Override
  public void run(GUIAnalysisOutput output) {
    VarUtil.v().guiOutput = output;
    Configs.debugCodes.add(Debug.DUMP_CCFX_DEBUG);
		String[] split = Configs.benchmarkName.split("/");
		String apkname = split[split.length - 1];
		WTGBuilder wtgBuilder = new WTGBuilder(apkname);
    // WTGBuilder wtgBuilder = new WTGBuilder();
    wtgBuilder.build(output);
    WTGAnalysisOutput wtgAO = new WTGAnalysisOutput(output, wtgBuilder);
    WTG wtg = wtgAO.getWTG();

    Collection<WTGEdge> edges = wtg.getEdges();
    Collection<WTGNode> nodes = wtg.getNodes();

    Multimap<NObjectNode, NObjectNode> guiHierarchy = wtgBuilder.guiHierarchy;
	Multimap<NObjectNode, HandlerBean> widgetToHandlers = wtgBuilder.widgetToHandlers;
	Multimap<NObjectNode, NIdNode> widgetToImages = wtgBuilder.widgetToImages;
	Map<NObjectNode, Set<NIdNode>> viewToLayoutIds = output.getSolver().getViewToLayoutIds();

    Logger.verb("DEMO", "Application: " + Configs.benchmarkName);
    Logger.verb("DEMO", "Launcher Node: " + wtg.getLauncherNode());
    Logger.verb("DEMO", "========================");
		Logger.verb("DEMO", "viewToLayoutIds: " + viewToLayoutIds);
		Logger.verb("DEMO", "========================");
		PrintWriter out = null;
    try {
			out = new PrintWriter(Paths.get(new File(".").getCanonicalPath(), "data", "output", apkname + ".json").toString());
			JSONArray wins = new JSONArray();
			for (WTGNode n : nodes) {
				JSONObject win = new JSONObject();
				wins.add(win);
				if (viewToLayoutIds.containsKey(n.getWindow())) {
					win.put("name", n.getWindow().toString() + viewToLayoutIds.get(n.getWindow()));
				} else {
					win.put("name", n.getWindow().toString());
				}
				JSONArray jsonviews = new JSONArray();
				win.put("views", jsonviews);
				Logger.verb("DEMO", "Current Node: " + n.getWindow().toString());
				Collection<NObjectNode> views = guiHierarchy.get(n.getWindow());
				for (NObjectNode view : views) {
					Collection<HandlerBean> handlers = widgetToHandlers.get(view);
					Logger.verb("DEMO", "View: " + view + " handler: " + handlers);
					JSONObject viewjson = new JSONObject();
					jsonviews.add(viewjson);
					viewjson.put("name", view.toString());
					JSONArray jsonhandlers = new JSONArray();
					viewjson.put("handlers", jsonhandlers);
					for (HandlerBean handlerBean : handlers) {
						JSONObject handlerjson = new JSONObject();
						jsonhandlers.add(handlerjson);
						handlerjson.put("event", handlerBean.getEvent().toString());
						JSONArray eventhandlers = new JSONArray();
						handlerjson.put("handlers", eventhandlers);
						for (SootMethod m : handlerBean.getHandlers()) {
							eventhandlers.add(m.toString());
						}
					}

					Collection<NIdNode> imageIds = widgetToImages.get(view);
					JSONArray images = new JSONArray();
					viewjson.put("images", images);
					for (NIdNode imageid : imageIds) {
						images.add(imageid.toString());
					}

				}

			}
			out.println(wins.toJSONString());
			out.close();
		} catch (Exception e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}
}
