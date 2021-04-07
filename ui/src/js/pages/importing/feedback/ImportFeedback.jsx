// @flow
// vendor
import React,
{
  useEffect,
  useRef,
  useState,
} from 'react';
// components
import OutputMessage from 'Components/output/OutputMessage';


type Props = {
  feedback: String,
}

const ImportFeedback = ({ feedback }: Props) => {
  const feedbackRef = useRef();
  const [scrollAtBottom, updateScrollAtBottom] = useState(true);

  const updateScrollTop = (evt) => {
    if ((evt.target.scrollHeight - 1000) > evt.target.scrollTop) {
      updateScrollAtBottom(false);
    } else {
      updateScrollAtBottom(true);
    }
  };

  useEffect(() => {
    if (feedbackRef.current && scrollAtBottom) {
      feedbackRef.current.scrollTop = feedbackRef.current.scrollHeight;
    }
  }, [feedback]);

  return (
    <div
      className="Importing__feedback"
      onScroll={(evt) => { updateScrollTop(evt); }}
      ref={feedbackRef}
    >
      <OutputMessage message={feedback} />
    </div>
  );
};


export default ImportFeedback;
