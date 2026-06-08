/* global React, ReactDOM, Header, Hero, Stats, WhyTape, Roadmap, BlogNews, PriceCTA, Footer */
function App() {
  return (
    <React.Fragment>
      <Header />
      <Hero />
      <Stats />
      <WhyTape />
      <Roadmap />
      <BlogNews />
      <PriceCTA />
      <Footer />
    </React.Fragment>
  );
}
ReactDOM.createRoot(document.getElementById("root")).render(<App />);
