/* $Id$ 
 *
 * PyXMLSec -- Python bindings for XML Security library (XMLSec)
 *
 * Copyright (C) 2003-2005 Easter-eggs, Valery Febvre
 * http://pyxmlsec.labs.libre-entreprise.org
 * 
 * Author: Valery Febvre <vfebvre@easter-eggs.com>
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 * 
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */

#include "xmlsecmod.h"

#include "xmlsec.h"

PyObject *xmlsec_Init(PyObject *self, PyObject *args) {
  return (wrap_int(xmlSecInit()));
}

PyObject *xmlsec_Shutdown(PyObject *self, PyObject *args) {
  return (wrap_int(xmlSecShutdown()));
}

PyObject *xmlsec_CheckVersionExact(PyObject *self, PyObject *args) {
  return (wrap_int(xmlSecCheckVersionExact()));
}

PyObject *xmlsec_CheckVersion(PyObject *self, PyObject *args) {
  return (wrap_int(xmlSecCheckVersion()));
}

PyObject *xmlsec_CheckVersionExt(PyObject *self, PyObject *args) {
  int major;
  int minor;
  int subminor;
  xmlSecCheckVersionMode mode;
  
  if (CheckArgs(args, "IIII:checkVersionExt")) {
    if(!PyArg_ParseTuple(args, (char *) "iiii:checkVersionExt",
			 &major, &minor, &subminor, &mode))
      return NULL;
  }
  else return NULL;

  return (wrap_int(xmlSecCheckVersionExt(major, minor, subminor, mode)));
}
