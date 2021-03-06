/*
 * PropertyManager.java - part of the GATOR project
 *
 * Copyright (c) 2018 The Ohio State University
 *
 * This file is distributed under the terms described in LICENSE in the
 * root directory.
 */
package presto.android.gui;

import com.google.common.base.Joiner;
import com.google.common.collect.Sets;
import presto.android.gui.graph.*;
import presto.android.xml.XMLParser;

import java.util.Iterator;
import java.util.Set;

public class PropertyManager {
  private static PropertyManager theInstance;

  XMLParser xml = XMLParser.Factory.getXMLParser();

  PropertyManager() {

  }

  public static synchronized PropertyManager v() {
    if (theInstance == null) {
      theInstance = new PropertyManager();
    }
    return theInstance;
  }

  // === public interfaces

  /*
   * Given an object node, returns possible values of its title.
   */
  public Set<String> getTextsOrTitlesOfView(NObjectNode view) {
    Iterator<NNode> textNodes = view.getTextNodes();
    Set<String> titles = Sets.newHashSet();
    while (textNodes.hasNext()) {
      NNode textNode = textNodes.next();
      String title = textNodeToString(textNode);
      if (title != null) {
        titles.add(title);
      }
    }
    return titles;
  }

  public final static String SEPARATOR = "8AwrACha";

//  public String getSpeciallySeparatedTextOrTitlesOfView(NObjectNode view) {
//    Set<String> titleSet = getTextsOrTitlesOfView(view);
//    if (titleSet == null || titleSet.isEmpty()) {
//      return null;
//    }
//    return Joiner.on(SEPARATOR).join(titleSet);
//  }

  public Set<String> getHintOfView(NObjectNode view) {
    Iterator<NNode> hintNodes = view.getHintNodes();
    Set<String> hints = Sets.newHashSet();
    while (hintNodes.hasNext()) {
      NNode textNode = hintNodes.next();
      String hint = textNodeToString(textNode);
      if (hint != null) {
        hints.add(hint);
      }
    }
    return hints;
  }

//  public String getSpeciallySeparatedHintOfView(NObjectNode view) {
//    Set<String> hintSet = getHintOfView(view);
//    if (hintSet == null || hintSet.isEmpty()) {
//      return null;
//    }
//    return Joiner.on(SEPARATOR).join(hintSet);
//  }

  public String textNodeToString(NNode textNode) {
    if (textNode instanceof NStringConstantNode) {
      return ((NStringConstantNode) textNode).value;
    } else if (textNode instanceof NStringIdNode) {
      Integer stringId = ((NStringIdNode) textNode).getIdValue();
      if (stringId == null) {
        return null;
      }
      return xml.getStringValue(stringId);
    } else if (textNode instanceof NStringBuilderNode) {
      return Joiner.on(SEPARATOR).join(((NStringBuilderNode) textNode).possibleValues);
    } else {
      throw new RuntimeException("Unknown textNode " + textNode);
    }
  }
}
