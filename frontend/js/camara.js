class GestorCamara {
  constructor(video, canvasCaptura) { this.video=video; this.canvas=canvasCaptura; this.stream=null; this.alTerminar=null; }
  async iniciar() {
    if (!navigator.mediaDevices?.getUserMedia) throw new Error('El navegador no permite usar la webcam');
    this.stream = await navigator.mediaDevices.getUserMedia({video:{width:{ideal:1280},height:{ideal:720}},audio:false});
    this.video.srcObject = this.stream;
    await this.video.play();
    const pista = this.stream.getVideoTracks()[0];
    pista.addEventListener('ended', () => this.alTerminar?.('La cámara se desconectó'));
  }
  detener() { this.stream?.getTracks().forEach(p=>p.stop()); this.stream=null; this.video.srcObject=null; }
  async capturar() {
    if (!this.stream || this.video.readyState < 2) return null;
    const ancho=this.video.videoWidth, alto=this.video.videoHeight;
    this.canvas.width=ancho; this.canvas.height=alto;
    this.canvas.getContext('2d').drawImage(this.video,0,0,ancho,alto);
    return new Promise(resolve=>this.canvas.toBlob(resolve,'image/jpeg',0.82));
  }
}
window.GestorCamara = GestorCamara;
