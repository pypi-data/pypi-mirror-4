# -*- coding: utf-8 -*-
""" Porting of GSMG.C
"""
import logging

from ginsfsm.compat import string_types
from .utils import string_to_bytearray

from .dl_list import (
    ListItem,
    DoubleList,
    dl_add,
    dl_first,
    dl_last,
    dl_next,
    dl_delete,
    )


class SegmError(Exception):
    """ Raised when Segm have problems."""


class GMsgError(Exception):
    """ Raised when GMsg have problems."""


class Segm(ListItem):
    def __init__(self, gmsg):
        super(Segm, self).__init__()
        #
        # El número actual de bytes sin procesar es (tail - head).
        # El máximo número de bytes que puede haber es 'segm_size'.
        # 'tail' no puede ser mayor que 'segm_size'
        #
        self.head = 0  # primer byte sin procesar. Usado para LECTURA
        self.tail = 0  # próximo byte a añadir. Usado para ESCRITURA (añadir)
        self.fixp = 0  # fixed pointer. Usado en ESCRITURA para sobreescribir

        #
        #  Calcula tamaño segmento
        #
        if gmsg.cur_size >= gmsg.max_size:
            msg = "segm_create(): MAXIMUM size reached (%d over %d)" % (
                gmsg.cur_size, gmsg.max_size)
            logging.warning(msg)
            raise SegmError(msg)  # Alcanzado máximo tamaño

        data_size = gmsg.max_size - gmsg.cur_size
        if data_size > gmsg.segm_size:
            data_size = gmsg.segm_size
        gmsg.cur_size += data_size

        self.segm_size = data_size
        # Datos allocados dinamicamente (segm_size)
        self.data = bytearray(data_size)


class GMsg(ListItem):
    def __init__(self, segm_size, max_size=0):
        self.segm_size = segm_size  # tamaño segmentos datos
        # tamaño máximo total, si es 0, igual a segm_size (like PACKET!!!)
        self.max_size = max_size if max_size > 0 else segm_size
        self.cur_size = 0  # tamaño total actual
        self.dl_segm = DoubleList()  # lista de segmentos de datos
        self.fix_segm = None  # SEGM segmento marked para escritura (OVERWRITE)
        self.rd_segm = None  # SEGM segmento de lectura
        self.sublen = 0  # submensaje. procesamiento parcial de un msg

        #
        #   Creo segmento inicial
        #
        try:
            segm = Segm(self)
        except SegmError:
            raise GMsgError("ERROR creating segm")
        dl_add(self.dl_segm, segm)
        self.reset_rd()
        self.reset_wr()

    def segm_create(self):
        """ Crea un segmento de datos de tamaño 'data_size'
            Retorna None if error
        """
        try:
            segm = Segm(self)
        except SegmError:
            return None

        return segm

    def reset_rd(self):
        """ Reset current READING pointer
        """
        #
        #  Set current segment to first segment
        #
        self.rd_segm = dl_first(self.dl_segm)

        #
        #  Set ALL current segment pointer to 0
        #
        segm = dl_first(self.dl_segm)
        while segm:
            segm.head = 0
            segm = dl_next(segm)

    def reset_wr(self):
        """ Reset current WRITING pointer
        """
        #
        #  Set current segment to first segment
        #
        self.fix_segm = dl_first(self.dl_segm)

        #
        #  Set ALL current segment pointer to 0
        #
        segm = dl_first(self.dl_segm)
        while segm:
            segm.tail = 0
            segm.fixp = 0
            segm.data = bytearray(segm.segm_size)  # memset()
            segm = dl_next(segm)

    def getchar(self):
        """ LECTURA o procesamient del mensaje.
            Saca un byte del message retornalo
            Retorna None si no hay más bytes
        """
        if not self.rd_segm:
            #
            #   No hay mas datos
            #
            return None

        while self.rd_segm:
            if self.rd_segm.head < self.rd_segm.tail:
                #
                #  Retorna el byte y eliminalo del segm
                #
                c = self.rd_segm.data[self.rd_segm.head]
                self.rd_segm.head += 1
                return c

            #
            #   No hay mas datos en el segm
            #   Intentalo en el siguiente
            #
            self.rd_segm = dl_next(self.rd_segm)

        return None

    def check_char(self):
        """ LECTURA o procesamient del mensaje.
            Consulta un byte del message y dejalo en 'c' (NO LO SACA DEL MSG)
            Retorna None si no hay mas bytes, y el caracter si lo hay.
        """
        if not self.rd_segm:
            return None

        while self.rd_segm:
            if self.rd_segm.head < self.rd_segm.tail:
                #
                #  Retorna el byte
                #
                c = self.rd_segm.data[self.rd_segm.head]
                return c

            #
            #   No hay mas datos en el segm
            #   Intentalo en el siguiente
            #
            self.rd_segm = dl_next(self.rd_segm)

        return None

    def cur_seg_rd(self):
        """  LECTURA : Devuelve segm lectura actual
        """
        if not self.rd_segm:
            return None
        return self.rd_segm.data[self.rd_segm.head:]

    def cur_seglen_rd(self):
        """  LECTURA : Devuelve ln segm lectura actual
        """
        if not self.rd_segm:
            return None
        return self.rd_segm.tail - self.rd_segm.head

    def next_seg_rd(self):
        """ LECTURA : Pon como actual el siguiente segm de lectura
            Retorna false si no hay mas.
        """
        if not self.rd_segm:
            return None
        self.rd_segm = dl_next(self.rd_segm)
        if self.rd_segm:
            return True
        else:
            return False

    def getdata(self, ln):
        """ LECTURA : Saca 'ln' bytes del self, moviendo los datos a 'data'
            desde la posición actual de lectura.
            NOO Retorna nº de bytes sacados
            Retorna los datos
        """
        if not self.rd_segm:
            return None

        data = bytearray()
        while self.rd_segm and ln > 0:
            if self.rd_segm.head < self.rd_segm.tail:
                seg_len = self.rd_segm.tail - self.rd_segm.head
                if seg_len >= ln:
                    #
                    #  Con los bytes de este segm hay suficiente
                    #
                    data = self.rd_segm.data[
                        self.rd_segm.head:self.rd_segm.head + ln]
                    self.rd_segm.head += ln
                    return data
                else:
                    #
                    #  Falta bytes con este segm
                    #
                    data += self.rd_segm.data[
                        self.rd_segm.head:self.rd_segm.head + seg_len]

                    self.rd_segm.head += seg_len
                    ln -= seg_len

            #
            #   No hay mas datos en el segm
            #   Intentalo en el siguiente
            #
            self.rd_segm = dl_next(self.rd_segm)

        #
        #   No hay mas datos
        #
        return data

    def subsetdata(self, ln):
        """ LECTURA : Fija 'ln' bytes para el submensaje
        """
        if ln < self.bytesleft():
            self.sublen = ln
            return True
        logging.warning("Not enough data for subsetdata: (%d over %d)" % (
                        ln, self.bytesleft()))
        self.sublen = 0
        return False

    def subgetdata(self, ln):
        """ LECTURA : Saca 'ln' bytes del SUB-MSG, moviendo los datos a 'data'
            desde la posición actual de lectura.
            Si 'data' es NULL simplemente se sacan los bytes,
            sin copiarlos a nada.
            Retorna TRUE si n§ de bytes sacados es 'ln'
        """
        if ln > self.sublen:
            #
            #   No hay suficientes datos en el sublen
            #
            return None
        self.sublen -= ln
        return self.getdata(ln)

    def remove_subdata(self):
        # LECTURA : Saca los bytes del SUB-MSG, eliminandolos
        return self.subgetdata(self, self.sublen)

    def putchar(self, c):
        """ ESCRITURA del mensaje.
            Añade un byte al final del mensaje
            Retorna numero bytes escritos.
        """
        return self.putdata(self, c, 1)

    def putdata(self, data, ln=0):
        """ ESCRITURA del mensaje.
            Añade 'ln' bytes al final del mensaje
            Retorna numero bytes escritos.
        """
        data = string_to_bytearray(data)
        if ln == 0:
            ln = len(data)
        seg_len = 0
        writted = 0

        while ln > 0:
            segm = dl_last(self.dl_segm)
            if not segm or segm.tail >= segm.segm_size:
                #
                #   Crea un nuevo segm
                #
                segm = self.segm_create()
                if not segm:
                    return writted
                dl_add(self.dl_segm, segm)

            seg_len = segm.segm_size - segm.tail
            if seg_len >= ln:
                #
                #   Hay espacio en este segm
                #
                segm.data[segm.tail:ln] = data[:ln]
                segm.tail += ln
                writted += ln
                return writted
            else:
                #
                #   NO suficiente espacio
                #   Guarda lo que quepa en el segmento actual
                #
                segm.data[segm.tail:seg_len] = data[:seg_len]
                segm.tail += seg_len
                ln -= seg_len
                data = data[seg_len:]
                writted += seg_len
                #
                #   Crea un nuevo segm
                #
                segm = self.segm_create()
                if not segm:
                    return writted
                dl_add(self.dl_segm, segm)
        return writted

    def unputdata(self, ln):
        """ DESESCRITURA del mensaje.
            Quita 'ln' bytes del final del mensaje
        """
        segm = dl_last(self.dl_segm)
        if not segm or segm.tail < ln:
            logging.error("gmsg_unputdata(): ERROR NO HAY SUFICIENTE LEN")
            return False
        segm.tail -= ln
        return True

    def new_segm(self):
        """ ESCRITURA del mensaje.
            Crea un nuevo segm para a€adir datos
            Retorna FALSE si error
        """
        segm = self.segm_create()
        if not segm:
            logging.debug("gmsg_new_segm(): ERROR CREANDO SEGMENTO")
            return False
        dl_add(self.dl_segm, segm)
        return True

    def cur_seg_wr(self):
        """ ESCRITURA del mensaje.
            Retorna actual pointer segm de escritura
        """
        segm = dl_last(self.dl_segm)
        if segm:
            return segm.data
        else:
            return None

    def cur_seglen_wr(self):
        """ ESCRITURA del mensaje.
            Retorna len of segm de escritura actual
        """
        segm = dl_last(self.dl_segm)
        if segm:
            return segm.tail
        else:
            return 0

    def insert_char(self, c):
        """ ESCRITURA del mensaje.
            Inserta al principio del mensaje
            !!! OJO QUE INSERTA EN head
            Retorna FALSE si error
        """
        return self.insert_data(self, c, 1)

    def insert_data(self, data, ln=0):
        """ ESCRITURA del mensaje.
            Inserta 'ln' bytes al principio del mensaje
            !!!OJO QUE SE INSERTA EN HEAD
            !! NO SE PUEDEN INSERTAR MAS BYTES QUE EL TAMAÑO DEL SEGMENTO!!!
            Retorna FALSE si error
        """
        data = string_to_bytearray(data)
        if ln == 0:
            ln = len(data)
        if ln > self.segm_size:
            logging.error("gmsg_insert_data(): DATA TOO LARGE %d", ln)
            return False

        segm = dl_first(self.dl_segm)
        if not segm:
            logging.error("ERROR gmsg_insert_data(): No first segm")
            return False

        seg_len = segm.segm_size - segm.tail
        if seg_len >= ln:
            #
            #   Hay espacio en este segm
            #
            #   Mueve todo el segm ln posiciones
            segm.data[ln:segm.tail + ln] = segm.data[0:segm.tail]
            segm.data[0:ln] = data[0:ln]
            segm.tail += ln
            return True
        logging.warning("Cannot insert data: full data.")
        return False  # NO debe pasar nunca por aqui

    def mark_pos_write(self):
        """ Marca actual posición de escritura de datos
        """
        #
        #  Get last segment
        #
        self.fix_segm = dl_last(self.dl_segm)

        #
        #  Get tail pointer
        #
        self.fix_segm.fixp = self.fix_segm.tail

    def overwrite_data(self, data, ln=0):
        """ ESCRITURA del mensaje.
            Sobreescribe en la marked (fixed) position
            Retorna FALSE si error
        """
        if not self.fix_segm:
            #
            #  No hay fixed segm
            #
            logging.error("ERROR gmsg_overwrite_data() NO FIXED SEGM")
            return 0

        data = string_to_bytearray(data)
        if ln == 0:
            ln = len(data)

        self.fix_segm = self.fix_segm
        while self.fix_segm and ln > 0:
            if self.fix_segm.fixp < self.fix_segm.tail:
                seg_len = self.fix_segm.tail - self.fix_segm.fixp
                if seg_len >= ln:
                    #
                    #  Hay espacio en este segm
                    #
                    pos = self.fix_segm.fixp
                    self.fix_segm.data[pos:pos + ln] = data[:ln]
                    self.fix_segm.fixp += ln
                    return True
                else:
                    #
                    #   NO suficiente espacio
                    #
                    pos = self.fix_segm.fixp
                    self.fix_segm.data[pos:pos + seg_len] = data[:seg_len]
                    self.fix_segm.fixp += seg_len
                    ln -= seg_len
                    data = data[seg_len:]

            #
            #   No espacio en el segm
            #   Intentalo en el siguiente
            #
            self.fix_segm = dl_next(self.fix_segm)

        return False  # can't override all

    def marked_bytes(self):
        """ ESCRITURA: numero total de bytes escritos
            desde la marca hasta el final
        """
        sum_len = 0

        segm = self.fix_segm
        if not segm:
            return 0
        sum_len = segm.tail - segm.fixp
        segm = dl_next(segm)

        while segm:
            seg_len = segm.tail - segm.fixp
            if seg_len > 0:
                sum_len += seg_len
            segm = dl_next(segm)
        return sum_len

    def bytesleft(self):
        """LECTURA: nº bytes pendientes de procesar
        """
        sum_len = 0

        if not self.rd_segm:
            #
            #   No hay mas datos para leer
            #
            return 0

        segm = self.rd_segm
        while segm:
            seg_len = segm.tail - segm.head
            if seg_len > 0:
                sum_len += seg_len
            segm = dl_next(segm)

        return sum_len

    def totalbytes(self):
        """ ESCRITURA: numero total de bytes escritos
        """
        sum_len = 0

        segm = dl_first(self.dl_segm)
        while segm:
            seg_len = segm.tail
            if seg_len > 0:
                sum_len += seg_len
            segm = dl_next(segm)
        return sum_len


def gmsg_remove(gmsg):
    """ Elimina paquete
    """

    #
    #  Libera los segmentos
    #
    while 1:
        segm = dl_first(gmsg.dl_segm)
        if segm is None:
            break
        dl_delete(gmsg.dl_segm, segm)

    del gmsg
