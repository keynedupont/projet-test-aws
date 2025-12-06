from projet.pipelines import make_dataset, make_features, train_model, evaluate_model

def test_pipeline_runs():
    make_dataset.run()
    make_features.run()
    train_model.run()
    evaluate_model.run()