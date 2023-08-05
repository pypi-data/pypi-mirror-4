# -*- encoding: utf-8 -*-
# Pilas engine - A video game framework.
#
# Copyright 2010 - Hugo Ruscitti
# License: LGPLv3 (see http://www.gnu.org/licenses/lgpl.html)
#
# Website - http://www.pilas-engine.com.ar

import pilas.utils

class Estudiante:
    """Representa la habilidad de poder realizar habiliadades y comportamientos."""

    def __init__(self):
        self._habilidades = []
        self.comportamiento_actual = None
        self.comportamientos = []
        self.repetir_comportamientos_por_siempre = False
        self.habilidades = ProxyHabilidades(self._habilidades)

    def aprender(self, classname, *k, **w):
        "Comienza a realizar una habilidad indicada por parametros."

        if self.tiene_habilidad(classname):
            self.eliminar_habilidad(classname)
            self.agregar_habilidad(classname, *k, **w)
        else:
            self.agregar_habilidad(classname, *k, **w)

    def agregar_habilidad(self, classname, *k, **w):
        objeto_habilidad = classname(self, *k, **w)
        self._habilidades.append(objeto_habilidad)

    def eliminar_habilidad(self, classname):
        """ Elimina una habilidad asociada a un Actor. """
        habilidad = self.obtener_habilidad(classname)

        if habilidad:
            self._habilidades.remove(habilidad)

    def tiene_habilidad(self, classname):
        "Comprueba si tiene la habildad indicada"
        habilidades_actuales = [habilidad.__class__ for habilidad in self._habilidades]
        return (classname in habilidades_actuales)

    def tiene_comportamiento(self, classname):
        "Comprueba si tiene el comportamiento indicado"
        comportamientos_actuales = [comportamiento.__class__ for comportamiento in self.comportamientos]
        return (classname in comportamientos_actuales)

    def obtener_habilidad(self, classname):
        """ Obtiene la habilidad asociada a un Actor.
        Devuelve None si no se encontró."""
        su_habilidad = None

        for habilidad in self._habilidades:
            if habilidad.__class__ == classname:
                su_habilidad = habilidad
                break

        return su_habilidad

    def hacer_luego(self, comportamiento, repetir_por_siempre=False):
        """Define un nuevo comportamiento para realizar al final.

        Los actores pueden tener una cadena de comportamientos, este
        metodo agrega el comportamiento al final de la cadena.
        """

        self.comportamientos.append(comportamiento)
        self.repetir_comportamientos_por_siempre = repetir_por_siempre

    def hacer(self, comportamiento):
        "Define el comportamiento para el actor de manera inmediata."
        self.comportamientos.append(comportamiento)
        self._adoptar_el_siguiente_comportamiento()

    def eliminar_habilidades(self):
        "Elimina todas las habilidades asociadas al actor."
        for h in self._habilidades:
            h.eliminar()

    def eliminar_comportamientos(self):
        "Elimina todos los comportamientos que tiene que hacer el actor."
        for c in self.comportamientos:
            c.eliminar()

    def actualizar_habilidades(self):
        for h in self._habilidades:
            h.actualizar()

    def actualizar_comportamientos(self):
        termina = None

        if self.comportamiento_actual:
            termina = self.comportamiento_actual.actualizar()

            if termina:
                if self.repetir_comportamientos_por_siempre:
                    self.comportamientos.append(self.comportamiento_actual)
                self._adoptar_el_siguiente_comportamiento()
        else:
            self._adoptar_el_siguiente_comportamiento()

    def _adoptar_el_siguiente_comportamiento(self):
        if self.comportamientos:
            self.comportamiento_actual = self.comportamientos.pop(0)
            self.comportamiento_actual.iniciar(self)
        else:
            self.comportamiento_actual = None


class ProxyHabilidades(object):

    def __init__(self, habilidades):
        self.habilidades = habilidades

    def __getattr__(self, name):

        su_habilidad = None

        for habilidad in self.habilidades:
            if habilidad.__class__.__name__ == name:
                su_habilidad = habilidad
                break
            
        if not su_habilidad:
            raise Exception("El actor no tiene asignada la habilidad " + name + 
                            ".\n No puede acceder mediante actor.habilidades." + name)

        return su_habilidad
