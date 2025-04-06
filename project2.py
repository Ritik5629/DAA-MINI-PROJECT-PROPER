import tkinter as tk
from tkinter import messagebox
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class CableOptimizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Network Cable Optimizer")
        self.root.geometry("1000x620")
        self.root.configure(bg="#E6ECEF")

        # Data structures to hold graph details
        self.graph = []
        self.nodes = set()
        self.nx_graph = nx.Graph()

        # ----------- LEFT: Input Section ------------
        self.input_frame = tk.LabelFrame(root, text="Add Network Connection", bg="#E6ECEF",
                                         font=("Arial", 13, "bold"), padx=15, pady=15, labelanchor="n")
        self.input_frame.grid(row=0, column=0, sticky="n", padx=15, pady=10)

        # Building 1
        tk.Label(self.input_frame, text="Building 1:", font=("Arial", 11), bg="#E6ECEF").grid(row=0, column=0, sticky="e", pady=5)
        self.building1_entry = tk.Entry(self.input_frame, width=22, font=("Arial", 11))
        self.building1_entry.grid(row=0, column=1, pady=5)

        # Building 2
        tk.Label(self.input_frame, text="Building 2:", font=("Arial", 11), bg="#E6ECEF").grid(row=1, column=0, sticky="e", pady=5)
        self.building2_entry = tk.Entry(self.input_frame, width=22, font=("Arial", 11))
        self.building2_entry.grid(row=1, column=1, pady=5)

        # Distance
        tk.Label(self.input_frame, text="Distance (m):", font=("Arial", 11), bg="#E6ECEF").grid(row=2, column=0, sticky="e", pady=5)
        self.distance_entry = tk.Entry(self.input_frame, width=22, font=("Arial", 11))
        self.distance_entry.grid(row=2, column=1, pady=5)

        # Buttons
        tk.Button(self.input_frame, text="Add Connection", command=self.add_connection,
                  bg="#4CAF50", fg="white", font=("Arial", 11), width=20).grid(row=3, column=0, columnspan=2, pady=(15, 5))

        tk.Button(self.input_frame, text="Find Optimal Layout", command=self.find_optimal_layout,
                  bg="#2196F3", fg="white", font=("Arial", 11), width=20).grid(row=4, column=0, columnspan=2, pady=5)

        # ----------- RIGHT: Graph Frame ------------
        self.graph_frame = tk.LabelFrame(root, text="Network Graph", bg="white",
                                         font=("Arial", 13, "bold"), padx=10, pady=10, labelanchor="n")
        self.graph_frame.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=10, pady=10)

        # Graph canvas using matplotlib
        self.figure, self.ax = plt.subplots(figsize=(5.5, 4.5))
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.graph_frame)
        self.canvas.get_tk_widget().pack(expand=True, fill="both")

        # ----------- BOTTOM LEFT: Output Section ------------
        self.output_frame = tk.LabelFrame(root, text="Output - Cable Layout", bg="#E6ECEF",
                                          font=("Arial", 13, "bold"), padx=15, pady=10, labelanchor="n")
        self.output_frame.grid(row=1, column=0, sticky="nw", padx=15, pady=5)

        self.output_text = tk.Text(self.output_frame, height=14, width=40, font=("Consolas", 10))
        self.output_text.pack()
        self.output_text.config(state=tk.DISABLED)

        # Grid configuration for resizing
        root.grid_columnconfigure(1, weight=1)
        root.grid_rowconfigure(0, weight=1)
        root.grid_rowconfigure(1, weight=1)

    # Add connection to graph
    def add_connection(self):
        building1 = self.building1_entry.get().strip()
        building2 = self.building2_entry.get().strip()
        distance = self.distance_entry.get().strip()

        if not (building1 and building2 and distance.isdigit()):
            messagebox.showerror("Error", "Please enter valid inputs!\n- Building names\n- Numeric distance")
            return

        distance = int(distance)
        self.graph.append((distance, building1, building2))
        self.nodes.update([building1, building2])
        self.nx_graph.add_edge(building1, building2, weight=distance)

        # Show added connection in output
        self.output_text.config(state=tk.NORMAL)
        self.output_text.insert(tk.END, f"{building1} ↔ {building2}: {distance}m\n")
        self.output_text.config(state=tk.DISABLED)

        # Clear fields and update graph
        messagebox.showinfo("Success", "Connection Added Successfully!")
        self.building1_entry.delete(0, tk.END)
        self.building2_entry.delete(0, tk.END)
        self.distance_entry.delete(0, tk.END)
        self.draw_graph()

    # Draw current graph
    def draw_graph(self):
        self.ax.clear()
        pos = nx.spring_layout(self.nx_graph)
        nx.draw(self.nx_graph, pos, ax=self.ax, with_labels=True, node_size=650,
                node_color="#90CAF9", font_size=9, font_weight="bold", edge_color="#616161")
        labels = nx.get_edge_attributes(self.nx_graph, 'weight')
        nx.draw_networkx_edge_labels(self.nx_graph, pos, edge_labels=labels, ax=self.ax, font_size=8)
        self.ax.set_title("Current Network Layout", fontsize=11)
        self.canvas.draw()

    # Find MST using Kruskal’s algorithm
    def find_optimal_layout(self):
        if not self.graph:
            messagebox.showerror("Error", "Please add connections first!")
            return

        mst = self.kruskal_algorithm()

        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, "Optimal Cable Layout (MST):\n")
        total_distance = 0
        for u, v, weight in mst:
            self.output_text.insert(tk.END, f"{u} ↔ {v}: {weight}m\n")
            total_distance += weight
        self.output_text.insert(tk.END, f"\nTotal Distance: {total_distance}m")
        self.output_text.config(state=tk.DISABLED)

        # Visualize MST
        mst_graph = nx.Graph()
        for u, v, weight in mst:
            mst_graph.add_edge(u, v, weight=weight)
        self.visualize_mst(mst_graph)

    # Show MST graph
    def visualize_mst(self, mst_graph):
        self.ax.clear()
        pos = nx.spring_layout(mst_graph)
        nx.draw(mst_graph, pos, ax=self.ax, with_labels=True, node_size=650,
                node_color="#A5D6A7", font_size=9, font_weight="bold", edge_color="#388E3C")
        labels = nx.get_edge_attributes(mst_graph, 'weight')
        nx.draw_networkx_edge_labels(mst_graph, pos, edge_labels=labels, ax=self.ax, font_size=8)
        self.ax.set_title("Optimal Network Layout (MST)", fontsize=11)
        self.canvas.draw()

    # Kruskal's algorithm implementation
    def kruskal_algorithm(self):
        self.graph.sort()
        parent = {}
        rank = {}

        def find(node):
            if parent[node] != node:
                parent[node] = find(parent[node])
            return parent[node]

        def union(node1, node2):
            root1 = find(node1)
            root2 = find(node2)
            if root1 != root2:
                if rank[root1] > rank[root2]:
                    parent[root2] = root1
                elif rank[root1] < rank[root2]:
                    parent[root1] = root2
                else:
                    parent[root2] = root1
                    rank[root1] += 1

        for node in self.nodes:
            parent[node] = node
            rank[node] = 0

        mst = []
        for weight, u, v in self.graph:
            if find(u) != find(v):
                union(u, v)
                mst.append((u, v, weight))
        return mst

# Run the GUI Application
root = tk.Tk()
app = CableOptimizer(root)
root.mainloop()
