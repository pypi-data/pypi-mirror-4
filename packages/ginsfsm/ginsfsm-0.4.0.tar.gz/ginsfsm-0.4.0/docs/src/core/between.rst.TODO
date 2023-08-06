Communication between GObjs, through processes and threads.
===========================================================

All gobjs can communicate (send and receive events) between them.
All gobjs belong to a gaplic, and one mission of the gaplic, is
proportionate a communicate system between them.

Communication between processes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
GAplic can be synonymous of `process`.
GAplic, like any process, can have running inside one o more threads,
which are GAplics too.

GinsFSM provides a communication system between all gaplics,
whether they are in the same or different machine.

.. graphviz::

    graph gaplics_threads_gobjs {
        graph [splines=true overlap=false];
        size="5.0"
        node [shape="box3d" penwidth=2 style=filled fillcolor="lightgray"];
        subgraph cluster_machine1 {
            label = "machine1";
            "GAplic1" [label="GAplic1 process\n\n\n"];
            "GAplic2" [label="GAplic2 process\n\n\n"];
        }
        subgraph cluster_machine2 {
            label = "machine2";
            "GAplic3" [label="GAplic3 process\n\n\n"];
        }
        "GAplic1" -- "GAplic2" [label="(comm between gaplics)" penwidth=3];
        "GAplic2" -- "GAplic3" [label="(comm between gaplics)" penwidth=3];
        "GAplic1" -- "GAplic3" [label="(comm between gaplics)" penwidth=3];
        }


Communication between threads
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
A GAplic process can have one o several threads.
Each thread has their own one main gaplic object.

GinsFSM provides a communication system between all gaplics,
whether they are in the same or different `thread`.

.. graphviz::

    graph GAplic {
        size="6.0"
        //graph [fontsize=30 labelloc="t" label="" splines=true overlap=false rankdir="LR"];
        graph [splines=true overlap=false];
        node [shape="box3d" penwidth=2 style=filled fillcolor="lightgray"];
        label="GAplic Process";
        subgraph cluster_thread_main {
            subgraph cluster_main_thread3 {
                graph [style="filled" splines=true overlap=true];
                label="Thread3";
                gaplic3 -- obj31;
                gaplic3 -- obj32;
                obj31 -- obj33;
            }
            subgraph cluster_main_thread2 {
                graph [style="filled" splines=true overlap=true];
                label="Thread2";
                gaplic2 -- obj21;
                gaplic2 -- obj22;
                obj21 -- obj23;
            }
            subgraph cluster_main_thread {
                graph [style="filled" splines=true overlap=true];
                label="Main Thread";
                gaplic1 -- obj11;
                gaplic1 -- obj12;
                obj11 -- obj13;
            }
        }
        gaplic1  -- gaplic2 [label="(comm between gaplics)" penwidth=3];
        gaplic1  -- gaplic3 [label="(comm between gaplics)" penwidth=3];
        gaplic2  -- gaplic3 [label="(comm between gaplics)" penwidth=3];
    }


Communication between gobjs
^^^^^^^^^^^^^^^^^^^^^^^^^^^
A gobj can be anonymous or named.
You can communicate with other anonymous gobjs of the same gaplic.
To communicate with gobjs from other gaplics (from other processes or threads),
these must be `named` gobjs.

Each main gaplic has a register of their own `named` gobjs.
When two gaplics connected them, they interchange their `named` gobjs.
Also, there are a specialized gaplic process, that acts as a DNS,
recollecting all `named` gobjs from all gaplics. This process listen
in a fixed range of ports, so all gaplics can search and find it, to register
their `named` gobjs, and search for another gobjs.
