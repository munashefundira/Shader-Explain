import React, { useRef, useEffect, useState } from 'react';
import * as THREE from 'three';

function ShaderVisualization({ shaderCode, shaderType }) {
  const canvasRef = useRef(null);
  const [renderError, setRenderError] = useState(null);

  useEffect(() => {
    if (!canvasRef.current) return;

    let scene, camera, renderer, geometry, material, mesh, animationId;

    try {
      scene = new THREE.Scene();
      scene.background = new THREE.Color(0x1a1a2e);

      camera = new THREE.PerspectiveCamera(
        75,
        canvasRef.current.clientWidth / canvasRef.current.clientHeight,
        0.1,
        1000
      );
      camera.position.z = 2;

      renderer = new THREE.WebGLRenderer({ 
        canvas: canvasRef.current,
        antialias: true 
      });
      renderer.setSize(canvasRef.current.clientWidth, canvasRef.current.clientHeight);

      if (shaderType === 'fragment') {
        geometry = new THREE.PlaneGeometry(2, 2);
      } else {
        geometry = new THREE.SphereGeometry(1, 32, 32);
      }

      let vertexShader, fragmentShader;

      if (shaderType === 'fragment') {
        vertexShader = `
          varying vec2 vUv;
          void main() {
            vUv = uv;
            gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
          }
        `;
        fragmentShader = convertToThreeJS(shaderCode);
      } else if (shaderType === 'vertex') {
        vertexShader = `
          varying vec3 vNormal;
          uniform float time;
          
          void main() {
            vNormal = normalize(normalMatrix * normal);
            vec3 pos = position;
            pos += normal * sin(pos.y * 3.0 + time) * 0.1;
            gl_Position = projectionMatrix * modelViewMatrix * vec4(pos, 1.0);
          }
        `;
        fragmentShader = `
          varying vec3 vNormal;
          void main() {
            vec3 light = vec3(0.5, 0.2, 1.0);
            light = normalize(light);
            float dProd = max(0.0, dot(vNormal, light));
            gl_FragColor = vec4(dProd, dProd * 0.5, dProd * 1.5, 1.0);
          }
        `;
      } else {
        vertexShader = `
          void main() {
            gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
          }
        `;
        fragmentShader = `
          void main() {
            gl_FragColor = vec4(0.5, 0.3, 0.8, 1.0);
          }
        `;
      }

      material = new THREE.ShaderMaterial({
        vertexShader: vertexShader,
        fragmentShader: fragmentShader,
        uniforms: {
          time: { value: 0 },
          resolution: { value: new THREE.Vector2(800, 600) }
        }
      });

      mesh = new THREE.Mesh(geometry, material);
      scene.add(mesh);

      const animate = () => {
        animationId = requestAnimationFrame(animate);
        
        if (material.uniforms.time) {
          material.uniforms.time.value += 0.01;
        }

        mesh.rotation.x += 0.005;
        mesh.rotation.y += 0.01;

        renderer.render(scene, camera);
      };

      animate();
      setRenderError(null);

    } catch (error) {
      console.error('Shader rendering error:', error);
      setRenderError(error.message);
    }

    return () => {
      if (animationId) {
        cancelAnimationFrame(animationId);
      }
      if (renderer) {
        renderer.dispose();
      }
      if (geometry) {
        geometry.dispose();
      }
      if (material) {
        material.dispose();
      }
    };
  }, [shaderCode, shaderType]);

  const convertToThreeJS = (code) => {
    let converted = code;
    
    if (!converted.includes('varying vec2 vUv') && converted.includes('vUv')) {
      converted = 'varying vec2 vUv;\n' + converted;
    }

    if (!converted.includes('uniform float time')) {
      converted = 'uniform float time;\n' + converted;
    }

    return converted;
  };

  return (
    <div className="visualization-container">
      <h2>🎨 Shader Visualization</h2>
      
      <div className="shader-info">
        <span className="shader-type-badge">
          {shaderType === 'vertex' ? '📐 Vertex Shader' : 
           shaderType === 'fragment' ? '🎨 Fragment Shader' : 
           '❓ Unknown Shader'}
        </span>
      </div>

      <div className="canvas-wrapper">
        {renderError ? (
          <div style={{ 
            height: '100%', 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center',
            flexDirection: 'column',
            color: '#ff6b6b',
            padding: '20px',
            textAlign: 'center'
          }}>
            <p style={{ fontSize: '1.2rem', marginBottom: '10px' }}>
              ⚠️ Shader Rendering Error
            </p>
            <p style={{ fontSize: '0.9rem', opacity: 0.8 }}>
              {renderError}
            </p>
          </div>
        ) : (
          <canvas 
            ref={canvasRef} 
            style={{ 
              width: '100%', 
              height: '100%',
              display: 'block',
              borderRadius: '8px'
            }}
          />
        )}
      </div>

      <div className="visualization-controls">
        <p style={{ fontSize: '0.85rem', color: '#666', textAlign: 'center', marginTop: '10px' }}>
          ✨ Real-time WebGL rendering with Three.js
        </p>
      </div>
    </div>
  );
}

export default ShaderVisualization;