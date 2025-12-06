import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os

def generate_figure_1():
    print("Generating Figure 1: Architecture...")
    fig, ax = plt.subplots(figsize=(10, 12))
    
    layers = [
        "1. Presentation Layer\n(Web/Mobile UI, Dashboards)",
        "2. Application Services Layer\n(Inventory, Order, Optimization Logic)",
        "3. Federated Learning Layer\n(Model Training, Gradient Aggregation)",
        "4. Blockchain Consensus Layer\n(PoDQ Consensus, Smart Contracts)",
        "5. Digital Twin Layer\n(Simulation, State Synchronization)",
        "6. IoT Integration Layer\n(Sensor Data Acquisition, Edge Processing)",
        "7. Data Persistence Layer\n(Local Databases, Ledger Storage)"
    ]
    
    colors = ['#E6F3FF', '#CCE5FF', '#99CCFF', '#66B2FF', '#3399FF', '#0080FF', '#0066CC']
    
    # Draw layers
    for i, layer in enumerate(layers):
        # Rectangle
        rect = patches.Rectangle((0.1, 0.85 - i*0.12), 0.8, 0.1, linewidth=1, edgecolor='black', facecolor=colors[i])
        ax.add_patch(rect)
        
        # Text
        ax.text(0.5, 0.9 - i*0.12, layer, horizontalalignment='center', verticalalignment='center', fontsize=12, fontweight='bold')

    # Add side arrows/annotations
    ax.annotate('User Interaction', xy=(0.05, 0.9), xytext=(-0.1, 0.9),
                arrowprops=dict(facecolor='black', shrink=0.05))
    
    ax.annotate('Physical World', xy=(0.05, 0.2), xytext=(-0.1, 0.2),
                arrowprops=dict(facecolor='black', shrink=0.05))

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    ax.set_title("FM-ERP Seven-Layer Modular Architecture", fontsize=16)
    
    output_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'paper', 'figures')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    plt.savefig(os.path.join(output_dir, 'figure_1_architecture.png'), dpi=300, bbox_inches='tight')
    plt.close()

def generate_figure_2():
    print("Generating Figure 2: Ports and Adapters...")
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Core Domain (Hexagon-ish)
    core = patches.RegularPolygon((0.5, 0.5), numVertices=6, radius=0.25, orientation=0, facecolor='#FFEB99', edgecolor='black')
    ax.add_patch(core)
    ax.text(0.5, 0.5, "Core Domain\n(Business Logic)", ha='center', va='center', fontweight='bold')
    
    # Primary Ports (Left)
    primary_ports = ["IInventoryService", "IOrderService", "IOptimizationService"]
    for i, port in enumerate(primary_ports):
        y = 0.7 - i*0.2
        # Port Interface
        circle = patches.Circle((0.28, y), 0.02, facecolor='white', edgecolor='black')
        ax.add_patch(circle)
        ax.text(0.25, y, port, ha='right', va='center', fontsize=9)
        
        # Adapter (Driver)
        rect = patches.Rectangle((0.05, y-0.05), 0.15, 0.1, facecolor='#D1E8E2', edgecolor='black')
        ax.add_patch(rect)
        ax.text(0.125, y, "Web UI / API", ha='center', va='center', fontsize=8)
        
        # Arrow
        ax.arrow(0.2, y, 0.06, 0, head_width=0.02, head_length=0.02, fc='k', ec='k')

    # Secondary Ports (Right)
    secondary_ports = [
        ("IBlockchainAdapter", "Hyperledger Fabric"),
        ("IFLAdapter", "Flower Framework"),
        ("IDTAdapter", "SimPy Simulation"),
        ("IIoTAdapter", "MQTT / Sensors")
    ]
    
    for i, (port, adapter) in enumerate(secondary_ports):
        y = 0.8 - i*0.2
        # Port Interface
        circle = patches.Circle((0.72, y), 0.02, facecolor='white', edgecolor='black')
        ax.add_patch(circle)
        ax.text(0.75, y, port, ha='left', va='center', fontsize=9)
        
        # Adapter (Driven)
        rect = patches.Rectangle((0.8, y-0.05), 0.15, 0.1, facecolor='#E2D1E8', edgecolor='black')
        ax.add_patch(rect)
        ax.text(0.875, y, adapter, ha='center', va='center', fontsize=8)
        
        # Arrow
        ax.arrow(0.5 + 0.22, 0.5, 0.72-(0.5+0.22), y-0.5, head_width=0.0, head_length=0.0, fc='k', ec='k', alpha=0) # Invisible guide
        # Draw arrow from core to port
        # Simplified: just lines from center area
        
        # Arrow out
        ax.arrow(0.74, y, 0.06, 0, head_width=0.02, head_length=0.02, fc='k', ec='k')

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    ax.set_title("Ports-and-Adapters (Hexagonal) Integration Pattern", fontsize=16)
    
    output_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'paper', 'figures')
    plt.savefig(os.path.join(output_dir, 'figure_2_ports_adapters.png'), dpi=300, bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    generate_figure_1()
    generate_figure_2()
