#!/usr/bin/env python3
import os
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    PageTemplate,
    Paragraph,
    Spacer,
    PageBreak,
    Table,
    TableStyle,
    Preformatted,
    ListFlowable,
    ListItem,
    NextPageTemplate,
)
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.graphics.shapes import Drawing, String, Rect, Line, Polygon, Circle
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie


class TocDocTemplate(BaseDocTemplate):
    """DocTemplate that auto-populates a TableOfContents from Heading paragraphs."""

    def __init__(self, filename, **kw):
        self.allowSplitting = 1
        BaseDocTemplate.__init__(self, filename, **kw)

        frame = Frame(
            self.leftMargin,
            self.bottomMargin,
            self.width,
            self.height,
            id="normal",
        )

        self.addPageTemplates([
            PageTemplate(id="Cover", frames=frame, onPage=self._on_first_page),
            PageTemplate(id="Body", frames=frame, onPage=self._on_later_pages),
        ])

    def afterFlowable(self, flowable):
        from reportlab.platypus import Paragraph

        if isinstance(flowable, Paragraph):
            style_name = flowable.style.name
            if style_name in ("Heading1", "Heading2", "Heading3"):
                level = {"Heading1": 0, "Heading2": 1, "Heading3": 2}[style_name]
                text = flowable.getPlainText()
                self.notify("TOCEntry", (level, text, self.page))

    def _on_first_page(self, canvas, doc):
        canvas.saveState()
        # No header on the cover page; just a subtle footer
        canvas.setFont("Helvetica", 9)
        canvas.setFillColor(colors.grey)
        canvas.drawRightString(
            doc.pagesize[0] - doc.rightMargin,
            doc.bottomMargin * 0.75,
            f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}",
        )
        canvas.restoreState()

    def _on_later_pages(self, canvas, doc):
        canvas.saveState()
        # Header
        canvas.setFont("Helvetica-Bold", 10)
        canvas.setFillColor(colors.HexColor("#1f4d7a"))
        canvas.drawString(doc.leftMargin, doc.pagesize[1] - doc.topMargin + 14, "ROS 2 Comprehensive Guide")
        canvas.setStrokeColor(colors.HexColor("#1f4d7a"))
        canvas.setLineWidth(0.5)
        canvas.line(doc.leftMargin, doc.pagesize[1] - doc.topMargin + 10, doc.pagesize[0] - doc.rightMargin, doc.pagesize[1] - doc.topMargin + 10)

        # Footer with page number
        canvas.setFont("Helvetica", 9)
        canvas.setFillColor(colors.grey)
        canvas.drawRightString(
            doc.pagesize[0] - doc.rightMargin,
            doc.bottomMargin * 0.75,
            f"Page {doc.page}",
        )
        canvas.restoreState()


def build_styles():
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="TitleCenter",
            parent=styles["Title"],
            alignment=1,
            spaceAfter=18,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Subtitle",
            parent=styles["Normal"],
            fontSize=12,
            textColor=colors.grey,
            alignment=1,
            spaceAfter=12,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Small",
            parent=styles["Normal"],
            fontSize=9,
            textColor=colors.grey,
        )
    )
    # Tweak existing heading styles instead of redefining
    styles["Heading1"].textColor = colors.HexColor("#1f4d7a")
    styles["Heading1"].spaceAfter = 8
    styles["Heading1"].spaceBefore = 16

    styles["Heading2"].textColor = colors.HexColor("#245a91")
    styles["Heading2"].spaceAfter = 6
    styles["Heading2"].spaceBefore = 12

    styles["Heading3"].textColor = colors.HexColor("#2b6aa7")
    styles["Heading3"].spaceAfter = 4
    styles["Heading3"].spaceBefore = 10

    # Tweak existing Code style
    styles["Code"].fontName = "Courier"
    styles["Code"].fontSize = 8.6
    styles["Code"].leading = 11
    styles["Code"].backColor = colors.whitesmoke
    styles["Code"].borderColor = colors.lightgrey
    styles["Code"].borderWidth = 0.25
    styles["Code"].borderPadding = 6
    styles["Code"].spaceBefore = 6
    styles["Code"].spaceAfter = 6

    styles.add(
        ParagraphStyle(
            name="TableHeader",
            parent=styles["Normal"],
            fontSize=9.5,
            textColor=colors.white,
            backColor=colors.HexColor("#1f4d7a"),
            alignment=1,
        )
    )
    return styles


def add_cover_page(story, styles):
    story.append(Spacer(1, 2.2 * cm))
    story.append(Paragraph("ROS 2 Comprehensive Guide", styles["TitleCenter"]))
    story.append(
        Paragraph(
            "Libraries, Classes, Architecture, Syntax, Examples, and Best Practices", styles["Subtitle"]
        )
    )
    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph("2025 Edition", styles["Small"]))
    story.append(Paragraph("Generated by AI Assistant", styles["Small"]))
    story.append(Spacer(1, 1.0 * cm))

    # Simple decorative diagram on the cover
    story.append(create_cover_diagram(width=420, height=140))

    story.append(Spacer(1, 1.2 * cm))
    story.append(Paragraph(
        "This document provides a deeply practical, example-driven tour through ROS 2 (Robot Operating System 2). "
        "It covers the key libraries, classes, structure, syntax, and behavioral outcomes with runnable examples. "
        "Use this as a quick reference, learning aid, and field guide for building reliable robotic software.",
        styles["Normal"],
    ))


def add_toc(story, styles):
    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph("Table of Contents", styles["Heading1"]))
    toc = TableOfContents()
    toc.levelStyles = [
        ParagraphStyle(fontSize=11, name="TOCLevel1", leftIndent=12, firstLineIndent=-12, spaceBefore=6),
        ParagraphStyle(fontSize=10, name="TOCLevel2", leftIndent=24, firstLineIndent=-12, spaceBefore=2),
        ParagraphStyle(fontSize=9, name="TOCLevel3", leftIndent=36, firstLineIndent=-12, spaceBefore=0),
    ]
    story.append(toc)


def create_cover_diagram(width=420, height=140):
    d = Drawing(width, height)

    # Background box
    d.add(Rect(0, 0, width, height, fillColor=colors.HexColor("#f4f8fb"), strokeColor=colors.HexColor("#d9e6f2")))

    # Nodes
    d.add(Rect(30, 50, 110, 60, fillColor=colors.white, strokeColor=colors.HexColor("#1f4d7a")))
    d.add(String(85, 80, "Node A", fontName="Helvetica", fontSize=10, textAnchor="middle", fillColor=colors.HexColor("#1f4d7a")))

    d.add(Rect(280, 50, 110, 60, fillColor=colors.white, strokeColor=colors.HexColor("#1f4d7a")))
    d.add(String(335, 80, "Node B", fontName="Helvetica", fontSize=10, textAnchor="middle", fillColor=colors.HexColor("#1f4d7a")))

    # Topic bus
    d.add(Rect(160, 60, 100, 40, fillColor=colors.HexColor("#e9f2fa"), strokeColor=colors.HexColor("#84a8c6")))
    d.add(String(210, 78, "Topic: /chatter", fontName="Helvetica", fontSize=9, textAnchor="middle", fillColor=colors.HexColor("#1f4d7a")))

    # Arrows
    d.add(Line(140, 80, 160, 80, strokeColor=colors.HexColor("#1f4d7a")))
    d.add(Polygon([156, 84, 160, 80, 156, 76], fillColor=colors.HexColor("#1f4d7a")))

    d.add(Line(260, 80, 280, 80, strokeColor=colors.HexColor("#1f4d7a")))
    d.add(Polygon([260, 84, 264, 80, 260, 76], fillColor=colors.HexColor("#1f4d7a")))

    return d


def add_heading(story, styles, text, level=1):
    style_name = {1: "Heading1", 2: "Heading2", 3: "Heading3"}[level]
    story.append(Paragraph(text, styles[style_name]))


def build_intro_section(story, styles):
    add_heading(story, styles, "Introduction", level=1)
    story.append(
        Paragraph(
            "ROS 2 is a modular, distributed framework for building robotic systems. It builds on DDS (Data Distribution Service) and offers "
            "publish–subscribe topics, synchronous services, asynchronous actions, parameters, lifecycle management, and a rich tooling ecosystem.",
            styles["Normal"],
        )
    )
    story.append(
        ListFlowable(
            [
                ListItem(Paragraph("Core paradigms: nodes, topics, services, actions, parameters, lifecycle", styles["Normal"])),
                ListItem(Paragraph("Language bindings: C++ (rclcpp) and Python (rclpy)", styles["Normal"])),
                ListItem(Paragraph("Transport: DDS vendors (CycloneDDS, Fast DDS, Connext) via rmw layer", styles["Normal"])),
                ListItem(Paragraph("Build and package: ament, colcon, CMake, and package.xml", styles["Normal"])),
                ListItem(Paragraph("CLI tooling: ros2 command for discovery, run, inspect, bag, doctor", styles["Normal"])),
            ],
            bulletType="bullet",
            start="circle",
        )
    )


def build_architecture_section(story, styles):
    add_heading(story, styles, "Architecture and Core Concepts", level=1)

    add_heading(story, styles, "Nodes and Execution", level=2)
    story.append(
        Paragraph(
            "A node is a process that uses ROS 2 client libraries. Executors spin nodes and dispatch callbacks from subscriptions, timers, and services.",
            styles["Normal"],
        )
    )

    add_heading(story, styles, "Topics (Publish–Subscribe)", level=2)
    story.append(
        Paragraph(
            "Topics are asynchronous data streams. Publishers write messages and subscribers receive them. QoS policies control delivery guarantees and history.",
            styles["Normal"],
        )
    )

    add_heading(story, styles, "Services (Request–Response)", level=2)
    story.append(
        Paragraph(
            "Services provide synchronous request/response RPC semantics between clients and servers.",
            styles["Normal"],
        )
    )

    add_heading(story, styles, "Actions (Long-running Goals)", level=2)
    story.append(
        Paragraph(
            "Actions split long-running tasks into goal, feedback, and result channels, allowing cancelation and progress updates.",
            styles["Normal"],
        )
    )

    add_heading(story, styles, "Parameters and Lifecycle", level=2)
    story.append(
        Paragraph(
            "Parameters are key/value configuration for nodes. Lifecycle nodes have managed states (unconfigured, inactive, active) enabling reliable bring-up.",
            styles["Normal"],
        )
    )

    story.append(Spacer(1, 0.3 * cm))
    story.append(create_architecture_diagram())
    story.append(Spacer(1, 0.2 * cm))

    # QoS overview table
    add_heading(story, styles, "Quality of Service (QoS)", level=2)
    qos_data = [
        [Paragraph("Policy", styles["TableHeader"]), Paragraph("Options", styles["TableHeader"]), Paragraph("Effect", styles["TableHeader"])],
        ["Reliability", "Reliable | Best Effort", "Delivery guarantees vs. speed"],
        ["Durability", "Volatile | Transient Local", "Late-joiners receive last samples with TL"],
        ["History", "Keep Last | Keep All", "How many messages to store in the queue"],
        ["Depth", "Integer >= 0", "Size of the message queue"],
        ["Deadline", "Duration", "Max allowable period between samples"],
        ["Lifespan", "Duration", "Validity period for messages"],
        ["Liveliness", "Automatic | Manual", "Node presence detection semantics"],
    ]
    qos_table = Table(qos_data, colWidths=[3.0 * cm, 6.0 * cm, 7.0 * cm])
    qos_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f4d7a")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("BOX", (0, 0), (-1, -1), 0.25, colors.grey),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    story.append(qos_table)

    story.append(Spacer(1, 0.2 * cm))
    story.append(create_qos_chart())


def create_architecture_diagram():
    """Schematic: Node A publishes to /scan; Node B subscribes; a service connects C<->D; an action between E<->F."""
    width, height = 480, 240
    d = Drawing(width, height)

    # Topic-based communication
    d.add(Rect(20, 140, 110, 60, strokeColor=colors.HexColor("#1f4d7a"), fillColor=colors.white))
    d.add(String(75, 170, "Node A", textAnchor="middle", fontSize=10, fillColor=colors.HexColor("#1f4d7a")))
    d.add(Rect(350, 140, 110, 60, strokeColor=colors.HexColor("#1f4d7a"), fillColor=colors.white))
    d.add(String(405, 170, "Node B", textAnchor="middle", fontSize=10, fillColor=colors.HexColor("#1f4d7a")))

    d.add(Rect(200, 152, 80, 36, strokeColor=colors.HexColor("#84a8c6"), fillColor=colors.HexColor("#e9f2fa")))
    d.add(String(240, 168, "Topic\n/scan", textAnchor="middle", fontSize=8, fillColor=colors.HexColor("#1f4d7a")))

    d.add(Line(130, 170, 200, 170, strokeColor=colors.HexColor("#1f4d7a")))
    d.add(Polygon([196, 174, 200, 170, 196, 166], fillColor=colors.HexColor("#1f4d7a")))

    d.add(Line(280, 170, 350, 170, strokeColor=colors.HexColor("#1f4d7a")))
    d.add(Polygon([350, 174, 354, 170, 350, 166], fillColor=colors.HexColor("#1f4d7a")))

    # Service communication
    d.add(Rect(20, 40, 110, 60, strokeColor=colors.HexColor("#16603c"), fillColor=colors.white))
    d.add(String(75, 70, "Node C", textAnchor="middle", fontSize=10, fillColor=colors.HexColor("#16603c")))

    d.add(Rect(350, 40, 110, 60, strokeColor=colors.HexColor("#16603c"), fillColor=colors.white))
    d.add(String(405, 70, "Node D", textAnchor="middle", fontSize=10, fillColor=colors.HexColor("#16603c")))

    d.add(String(240, 90, "Service: /get_map", textAnchor="middle", fontSize=8, fillColor=colors.HexColor("#16603c")))

    # Bidirectional arrows
    d.add(Line(130, 70, 350, 70, strokeColor=colors.HexColor("#16603c")))
    d.add(Polygon([346, 74, 350, 70, 346, 66], fillColor=colors.HexColor("#16603c")))
    d.add(Polygon([134, 74, 130, 70, 134, 66], fillColor=colors.HexColor("#16603c")))

    # Action communication (goal/feedback/result)
    d.add(Circle(240, 110, 8, strokeColor=colors.HexColor("#9a5c0a"), fillColor=colors.HexColor("#f4e8d6")))
    d.add(String(240, 110, "A", textAnchor="middle", fontSize=7, fillColor=colors.HexColor("#9a5c0a")))
    d.add(String(240, 124, "Action: /nav", textAnchor="middle", fontSize=8, fillColor=colors.HexColor("#9a5c0a")))

    return d


def create_qos_chart():
    """Simple dataset visualization for QoS usage choices."""
    drawing = Drawing(480, 200)

    chart = VerticalBarChart()
    chart.x = 40
    chart.y = 40
    chart.height = 120
    chart.width = 400

    chart.data = [
        [70, 40, 55, 30],  # Reliable
        [30, 60, 45, 70],  # Best Effort
    ]
    chart.categoryAxis.categoryNames = ["Control", "Video", "Telemetry", "Debug"]
    chart.barWidth = 12
    chart.groupSpacing = 12
    chart.valueAxis.valueMin = 0
    chart.valueAxis.valueMax = 100
    chart.valueAxis.valueStep = 20

    chart.bars[0].fillColor = colors.HexColor("#1f4d7a")
    chart.bars[1].fillColor = colors.HexColor("#84a8c6")

    drawing.add(chart)

    # Legend-like labels
    drawing.add(String(360, 170, "Reliable", fontSize=9, fillColor=colors.HexColor("#1f4d7a")))
    drawing.add(Rect(340, 166, 14, 8, fillColor=colors.HexColor("#1f4d7a"), strokeColor=colors.HexColor("#1f4d7a")))
    drawing.add(String(440, 170, "Best Effort", fontSize=9, fillColor=colors.HexColor("#84a8c6")))
    drawing.add(Rect(420, 166, 14, 8, fillColor=colors.HexColor("#84a8c6"), strokeColor=colors.HexColor("#84a8c6")))

    return drawing


def build_api_reference_section(story, styles):
    add_heading(story, styles, "Client Libraries and Key Classes", level=1)

    add_heading(story, styles, "C++ (rclcpp)", level=2)
    cpp_rows = [
        [Paragraph("Class", styles["TableHeader"]), Paragraph("Purpose", styles["TableHeader"]), Paragraph("Key API", styles["TableHeader"])],
        [
            "rclcpp::Node",
            "Represents a ROS 2 node (parameters, logging, time)",
            "Node(name), get_logger(), declare_parameter(), create_publisher<T>(), create_subscription<T>()",
        ],
        [
            "rclcpp::Publisher<T>",
            "Publishes messages on a topic",
            "publish(msg), get_topic_name()",
        ],
        [
            "rclcpp::Subscription<T>",
            "Receives messages from a topic",
            "Callback signature: void(const T::SharedPtr&)",
        ],
        [
            "rclcpp::Service<T> / rclcpp::Client<T>",
            "Service server/client for request/response",
            "create_service<T>(srv, cb), create_client<T>(srv)",
        ],
        [
            "rclcpp_action::Server<T> / Client<T>",
            "Action server/client for long-running tasks",
            "async_send_goal(), handle_accepted(), publish_feedback()",
        ],
        [
            "rclcpp::executors::SingleThreadedExecutor",
            "Executes callbacks on one thread",
            "add_node(), spin()",
        ],
        [
            "rclcpp::executors::MultiThreadedExecutor",
            "Executes callbacks on a pool of threads",
            "add_node(), spin()",
        ],
        [
            "rclcpp::TimerBase",
            "Periodic callbacks",
            "create_wall_timer(period, cb)",
        ],
        [
            "rclcpp::QoS",
            "QoS profiles (reliability, durability, depth)",
            "QoS(depth).reliable(), keep_last(n)",
        ],
        [
            "rclcpp_lifecycle::LifecycleNode",
            "Managed lifecycle with states and transitions",
            "on_configure(), on_activate(), on_shutdown()",
        ],
    ]
    cpp_table = Table(cpp_rows, colWidths=[5.2 * cm, 6.0 * cm, 5.8 * cm])
    cpp_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f4d7a")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("BOX", (0, 0), (-1, -1), 0.25, colors.grey),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    story.append(cpp_table)

    add_heading(story, styles, "Python (rclpy)", level=2)
    py_rows = [
        [Paragraph("Class", styles["TableHeader"]), Paragraph("Purpose", styles["TableHeader"]), Paragraph("Key API", styles["TableHeader"])],
        [
            "rclpy.node.Node",
            "ROS 2 node abstraction (parameters, logging, time)",
            "Node(name), get_logger(), declare_parameter(), create_publisher(), create_subscription()",
        ],
        [
            "Publisher",
            "Publishes messages on a topic",
            "publish(msg), topic_name",
        ],
        [
            "Subscription",
            "Receives messages from a topic",
            "callback(msg)",
        ],
        [
            "Client / Service",
            "Request/response interactions",
            "create_client(srv, name), create_service(srv, name, cb)",
        ],
        [
            "Timer",
            "Periodic callbacks",
            "create_timer(seconds, cb)",
        ],
        [
            "QoSProfile",
            "QoS policies for topics",
            "QoSProfile(depth=n, reliability=..., durability=...)",
        ],
        [
            "LifecycleNode (rclpy.lifecycle)",
            "Managed states for reliable bring-up",
            "on_configure(), on_activate(), on_shutdown()",
        ],
    ]
    py_table = Table(py_rows, colWidths=[5.2 * cm, 6.0 * cm, 5.8 * cm])
    py_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f4d7a")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("BOX", (0, 0), (-1, -1), 0.25, colors.grey),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    story.append(py_table)


def build_examples_section(story, styles):
    add_heading(story, styles, "Examples and Expected Output", level=1)

    add_heading(story, styles, "Minimal Publisher (Python)", level=2)
    code_py_pub = """
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class MinimalPublisher(Node):
    def __init__(self):
        super().__init__('minimal_publisher')
        self.publisher_ = self.create_publisher(String, 'chatter', 10)
        self.timer = self.create_timer(0.5, self.timer_callback)
        self.count = 0

    def timer_callback(self):
        msg = String()
        msg.data = f'Hello ROS 2: {self.count}'
        self.publisher_.publish(msg)
        self.get_logger().info(f'Publishing: {msg.data}')
        self.count += 1

def main():
    rclpy.init()
    node = MinimalPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
"""
    story.append(Preformatted(code_py_pub.strip(), styles["Code"]))
    story.append(Paragraph("Expected output (console):", styles["Italic"]))
    story.append(Preformatted("""
[INFO] [minimal_publisher]: Publishing: Hello ROS 2: 0
[INFO] [minimal_publisher]: Publishing: Hello ROS 2: 1
... (repeats)
""".strip(), styles["Code"]))

    add_heading(story, styles, "Minimal Subscriber (Python)", level=2)
    code_py_sub = """
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class MinimalSubscriber(Node):
    def __init__(self):
        super().__init__('minimal_subscriber')
        self.subscription = self.create_subscription(String, 'chatter', self.listener_callback, 10)
        self.subscription  # prevent unused variable warning

    def listener_callback(self, msg: String):
        self.get_logger().info(f'I heard: {msg.data}')


def main():
    rclpy.init()
    node = MinimalSubscriber()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
"""
    story.append(Preformatted(code_py_sub.strip(), styles["Code"]))
    story.append(Paragraph("Expected output (console):", styles["Italic"]))
    story.append(Preformatted("""
[INFO] [minimal_subscriber]: I heard: Hello ROS 2: 0
[INFO] [minimal_subscriber]: I heard: Hello ROS 2: 1
... (repeats)
""".strip(), styles["Code"]))

    add_heading(story, styles, "Minimal Publisher (C++)", level=2)
    code_cpp_pub = r"""
#include <chrono>
#include <memory>
#include <rclcpp/rclcpp.hpp>
#include <std_msgs/msg/string.hpp>

using namespace std::chrono_literals;

class MinimalPublisher : public rclcpp::Node {
public:
    MinimalPublisher() : Node("minimal_publisher"), count_(0) {
        publisher_ = this->create_publisher<std_msgs::msg::String>("chatter", 10);
        timer_ = this->create_wall_timer(500ms, std::bind(&MinimalPublisher::on_timer, this));
    }
private:
    void on_timer() {
        auto message = std_msgs::msg::String();
        message.data = "Hello ROS 2: " + std::to_string(count_++);
        publisher_->publish(message);
        RCLCPP_INFO(this->get_logger(), "Publishing: %s", message.data.c_str());
    }
    rclcpp::Publisher<std_msgs::msg::String>::SharedPtr publisher_;
    rclcpp::TimerBase::SharedPtr timer_;
    size_t count_;
};

int main(int argc, char ** argv) {
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<MinimalPublisher>());
    rclcpp::shutdown();
    return 0;
}
"""
    story.append(Preformatted(code_cpp_pub.strip(), styles["Code"]))

    add_heading(story, styles, "Service (Python): AddTwoInts", level=2)
    code_py_srv = """
import rclpy
from rclpy.node import Node
from example_interfaces.srv import AddTwoInts

class AddTwoIntsServer(Node):
    def __init__(self):
        super().__init__('add_two_ints_server')
        self.srv = self.create_service(AddTwoInts, 'add_two_ints', self.add)

    def add(self, request, response):
        response.sum = request.a + request.b
        self.get_logger().info(f'Req: a={request.a} b={request.b} -> {response.sum}')
        return response


def main():
    rclpy.init()
    node = AddTwoIntsServer()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
"""
    story.append(Preformatted(code_py_srv.strip(), styles["Code"]))
    story.append(Paragraph("Example client call:", styles["Italic"]))
    story.append(Preformatted("""
ros2 service call /add_two_ints example_interfaces/srv/AddTwoInts "{a: 2, b: 40}"
""".strip(), styles["Code"]))
    story.append(Paragraph("Expected output (console):", styles["Italic"]))
    story.append(Preformatted("""
[INFO] [add_two_ints_server]: Req: a=2 b=40 -> 42
""".strip(), styles["Code"]))

    add_heading(story, styles, "Actions (Conceptual)", level=2)
    story.append(
        Paragraph(
            "Use rclcpp_action or rclpy action interfaces for long-running goals. Define a Goal, Feedback, and Result type. Clients send goals asynchronously; servers report feedback and results.",
            styles["Normal"],
        )
    )


def build_cli_build_section(story, styles):
    add_heading(story, styles, "CLI and Build System", level=1)

    add_heading(story, styles, "Create a Package", level=2)
    story.append(Preformatted(
        """
# C++ package
ros2 pkg create --build-type ament_cmake --dependencies rclcpp std_msgs my_cpp_pkg

# Python package
ros2 pkg create --build-type ament_python --dependencies rclpy std_msgs my_py_pkg
""".strip(),
        styles["Code"],
    ))

    add_heading(story, styles, "Build and Run", level=2)
    story.append(Preformatted(
        """
colcon build --symlink-install
source install/setup.bash
ros2 run my_cpp_pkg my_node
ros2 run my_py_pkg my_node
""".strip(),
        styles["Code"],
    ))

    add_heading(story, styles, "Discovery and Introspection", level=2)
    story.append(Preformatted(
        """
ros2 node list
ros2 topic list
ros2 topic echo /chatter
ros2 interface show std_msgs/msg/String
ros2 doctor --report
""".strip(),
        styles["Code"],
    ))


def build_package_structure_section(story, styles):
    add_heading(story, styles, "Package Structure", level=1)

    add_heading(story, styles, "C++ (ament_cmake)", level=2)
    story.append(Preformatted(
        """
my_cpp_pkg/
  CMakeLists.txt
  package.xml
  src/
    minimal_publisher.cpp
  include/my_cpp_pkg/
    minimal_publisher.hpp
  launch/
    demo.launch.py
""".strip(),
        styles["Code"],
    ))

    add_heading(story, styles, "Python (ament_python)", level=2)
    story.append(Preformatted(
        """
my_py_pkg/
  package.xml
  setup.cfg
  setup.py
  resource/
    my_py_pkg
  my_py_pkg/
    __init__.py
    minimal_publisher.py
  launch/
    demo.launch.py
""".strip(),
        styles["Code"],
    ))


def build_launch_section(story, styles):
    add_heading(story, styles, "Launch Files", level=1)
    story.append(
        Paragraph(
            "Launch files orchestrate multiple nodes and parameters. Use Python-based launch descriptions for flexibility.",
            styles["Normal"],
        )
    )
    story.append(Preformatted(
        """
# demo.launch.py
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(package='my_py_pkg', executable='minimal_publisher', name='talker', parameters=[{'use_sim_time': False}]),
        Node(package='my_py_pkg', executable='minimal_subscriber', name='listener'),
    ])
""".strip(),
        styles["Code"],
    ))


def build_testing_section(story, styles):
    add_heading(story, styles, "Testing", level=1)
    story.append(
        Paragraph(
            "Use gtest for C++ and pytest or launch_testing for Python. Integrate with colcon test.",
            styles["Normal"],
        )
    )
    story.append(Preformatted(
        """
# C++ (gtest) snippet
TEST(TestTopic, Publishes) {
  // Build node, publish, spin, assert received
}

# Python (pytest) example
import pytest

def test_add_two_ints_client():
    assert 2 + 40 == 42

# Run
colcon test --ctest-args -R my_pkg
colcon test-result --verbose
""".strip(),
        styles["Code"],
    ))


def build_best_practices_section(story, styles):
    add_heading(story, styles, "Performance, Reliability, and Best Practices", level=1)

    bullets = [
        "Prefer composition (components) to reduce process overhead and enable zero-copy intra-process communication.",
        "Choose QoS consciously: Reliable for control and critical telemetry; Best Effort for high-rate, lossy streams (e.g., video).",
        "Use executors appropriate to workload: MultiThreadedExecutor for IO-bound callbacks; SingleThreaded for deterministic order.",
        "Pin CPU cores and use real-time kernels for hard real-time; avoid dynamic memory in critical loops.",
        "Leverage loaned messages and intra-process communication to minimize copies (where supported).",
        "Record and replay with rosbag2 for debugging and regression testing.",
        "Trace with ros2_tracing/LTTng and profile callback latencies.",
        "Secure DDS with DDS-Security (encryption, authentication) when on untrusted networks.",
        "Use parameters with descriptors, declare early, and validate on set callbacks.",
        "Organize packages cleanly; keep message definitions in separate interface packages.",
        "Document interface contracts and QoS for each topic/service/action.",
    ]
    story.append(ListFlowable([ListItem(Paragraph(b, styles["Normal"])) for b in bullets], bulletType="bullet", start="square"))

    story.append(Spacer(1, 0.2 * cm))
    story.append(create_distribution_pie())


def create_distribution_pie():
    drawing = Drawing(360, 220)
    pie = Pie()
    pie.x = 60
    pie.y = 40
    pie.width = 200
    pie.height = 200
    pie.data = [40, 35, 15, 10]
    pie.labels = ["Control", "Perception", "Navigation", "Tools"]
    pie.slices[0].fillColor = colors.HexColor("#1f4d7a")
    pie.slices[1].fillColor = colors.HexColor("#84a8c6")
    pie.slices[2].fillColor = colors.HexColor("#2b6aa7")
    pie.slices[3].fillColor = colors.HexColor("#a3b9cd")

    drawing.add(String(60, 18, "Typical ROS 2 workload focus per subsystem (illustrative)", fontSize=9, fillColor=colors.grey))
    drawing.add(pie)
    return drawing


def build_resources_section(story, styles):
    add_heading(story, styles, "Resources and Further Reading", level=1)
    story.append(
        ListFlowable(
            [
                ListItem(Paragraph("ROS 2 Tutorials (docs.ros.org)", styles["Normal"])),
                ListItem(Paragraph("Design articles and REP documents", styles["Normal"])),
                ListItem(Paragraph("DDS vendor docs (CycloneDDS, Fast DDS)", styles["Normal"])),
                ListItem(Paragraph("rosbag2, launch, composition, and tracing repositories", styles["Normal"])),
            ],
            bulletType="bullet",
            start="circle",
        )
    )


def build_glossary_section(story, styles):
    add_heading(story, styles, "Glossary", level=1)
    data = [
        [Paragraph("Term", styles["TableHeader"]), Paragraph("Definition", styles["TableHeader"])],
        ["DDS", "Data Distribution Service: the transport layer used by ROS 2"],
        ["rmw", "ROS middleware abstraction that bridges client libraries to DDS"],
        ["QoS", "Policies influencing message delivery semantics"],
        ["Executor", "Runs callbacks for one or more nodes"],
        ["Lifecycle", "Managed node states for predictable startup/shutdown"],
    ]
    tbl = Table(data, colWidths=[3.0 * cm, 13.0 * cm])
    tbl.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f4d7a")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("BOX", (0, 0), (-1, -1), 0.25, colors.grey),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    story.append(tbl)



def build_document(output_path: str):
    styles = build_styles()

    doc = TocDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=1.8 * cm,
        rightMargin=1.8 * cm,
        topMargin=1.6 * cm,
        bottomMargin=1.6 * cm,
        title="ROS 2 Comprehensive Guide",
        author="AI Assistant",
        subject="ROS 2 libraries, classes, structure, syntax, examples",
    )

    story = []

    # Cover
    add_cover_page(story, styles)

    # Switch to body template after cover
    story.append(NextPageTemplate("Body"))
    story.append(PageBreak())

    add_toc(story, styles)

    # Main content
    build_intro_section(story, styles)
    build_architecture_section(story, styles)
    build_api_reference_section(story, styles)
    build_examples_section(story, styles)
    build_cli_build_section(story, styles)
    build_package_structure_section(story, styles)
    build_launch_section(story, styles)
    build_testing_section(story, styles)
    build_best_practices_section(story, styles)
    build_glossary_section(story, styles)
    build_resources_section(story, styles)

    doc.build(story)


if __name__ == "__main__":
    output_dir = "/workspace/docs"
    os.makedirs(output_dir, exist_ok=True)
    output_pdf = os.path.join(output_dir, "ROS2_Comprehensive_Guide.pdf")
    build_document(output_pdf)
    print(f"Wrote: {output_pdf}")