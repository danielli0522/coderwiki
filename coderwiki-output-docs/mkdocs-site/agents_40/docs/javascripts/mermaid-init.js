document.addEventListener('DOMContentLoaded', function() {
    // 初始化 Mermaid
    if (typeof mermaid !== 'undefined') {
        mermaid.initialize({
            startOnLoad: true,
            theme: 'default',
            securityLevel: 'loose',
            flowchart: {
                useMaxWidth: true,
                htmlLabels: true
            },
            sequence: {
                useMaxWidth: true,
                diagramMarginX: 50,
                diagramMarginY: 10,
                actorMargin: 50,
                width: 150,
                height: 65,
                boxMargin: 10,
                boxTextMargin: 5,
                noteMargin: 10,
                messageMargin: 35,
                mirrorActors: true,
                bottomMarginAdj: 1,
                useMaxWidth: true
            }
        });

        // 手动渲染所有 mermaid 图表
        setTimeout(function() {
            const mermaidElements = document.querySelectorAll('pre.mermaid');
            mermaidElements.forEach(function(element, index) {
                const graphDefinition = element.textContent || element.innerText;
                const graphId = 'mermaid-' + index;
                
                // 创建一个新的 div 来放置渲染的图表
                const mermaidDiv = document.createElement('div');
                mermaidDiv.className = 'mermaid';
                mermaidDiv.id = graphId;
                mermaidDiv.textContent = graphDefinition;
                
                // 替换原来的 pre 元素
                element.parentNode.replaceChild(mermaidDiv, element);
            });
            
            // 重新渲染
            mermaid.init(undefined, '.mermaid');
        }, 100);
    }
});